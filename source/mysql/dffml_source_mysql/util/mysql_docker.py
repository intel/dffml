import os
import ssl
import shutil
import atexit
import socket
import pathlib
import logging
import tempfile
import subprocess
from contextlib import contextmanager
from typing import Optional

import docker

LOGGER = logging.getLogger(__package__)

logging.basicConfig(level=logging.DEBUG)

DOCKER_IMAGE = "mysql:8.0"
# MySQL daemons default listing port
DEFAULT_PORT = 3306
# Environment variables passed to MySQL container
DOCKER_ENV = {
    "MYSQL_DATABASE": "db",
    "MYSQL_USER": "user",
    "MYSQL_PASSWORD": "pass",
    "MYSQL_RANDOM_ROOT_PASSWORD": "yes",
}
# MySQL server config file
MY_CONF = """[mysqld]
have_ssl=YES
ssl_ca=/conf/certs/ca.pem
ssl_cert=/conf/certs/ca.pem
ssl_key=/conf/certs/server.key
require_secure_transport=ON
"""
DOCKER_NA: str = "Failed to connect to docker daemon"
DOCKER_AVAILABLE: bool = False
try:
    DOCKER_CLIENT: docker.DockerClient = docker.from_env()
    DOCKER_AVAILABLE = DOCKER_CLIENT.ping()
    DOCKER_CLIENT.close()
except:
    pass


class MySQLFailedToStart(Exception):
    pass  # pragma: no cov


def check_connection(addr: str, port: int, *, timeout: float = 0.1) -> bool:
    """
    Attempt to make a TCP connection. Return if a connection was made in
    less than ``timeout`` seconds. Return True if a connection is made within
    the timeout.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((addr, port))
        except:
            return False
    return True


def mkcleanup(docker_client, container):
    """
    Create a function which will remove the temporary file and stop the
    container. The function will register itself with the :py:`atexit` module to
    ensure that the container is stopped before Python exits. It will unregister
    itself whenever it is called.
    """
    func = None

    def cleanup():
        atexit.unregister(func)
        try:
            container.stop()
            container.wait()
        except:
            pass
        docker_client.close()

    func = cleanup
    atexit.register(func)
    return cleanup


@contextmanager
def mysql(*, sql_setup: Optional[str] = None):
    """
    Start a MySQL container and yield the IP of the container once ready for
    connections. ``sql_setup`` should be the .sql file used to initialize the
    database.
    """

    docker_client: docker.DockerClient = docker.from_env()
    with tempfile.TemporaryDirectory() as tempdir:
        # Create server config
        sql_conf_path = pathlib.Path(tempdir, "my.conf")
        sql_conf_path.write_text(MY_CONF)
        sql_conf_path.chmod(0o660)
        # Create cert folder
        cert_dir_path = pathlib.Path(tempdir, "certs")
        cert_dir_path.mkdir(mode=0o755)
        # Dump out SQL query to file
        if sql_setup is not None:
            sql_setup_path = pathlib.Path(tempdir, "dump.sql")
            sql_setup_path.write_text(sql_setup)
            sql_setup_path.chmod(0o555)
        # Tell the docker daemon to start MySQL
        LOGGER.debug("Starting MySQL...")
        container = docker_client.containers.run(
            DOCKER_IMAGE,
            command="bash -c 'while ! test -f /conf/certs/ready; do sleep 0.1; done; chown mysql:mysql /etc/my.conf; ls -lAF /etc/my.conf; cat /etc/my.conf; chown mysql:mysql /conf/certs/*; ls -lAF /conf/certs/; bash -xe /entrypoint.sh mysqld'",
            environment=DOCKER_ENV,
            detach=True,
            auto_remove=True,
            volumes={
                sql_conf_path.resolve(): {"bind": "/etc/my.conf"},
                sql_setup_path.resolve(): {
                    "bind": "/docker-entrypoint-initdb.d/dump.sql"
                },
                cert_dir_path.resolve(): {"bind": "/conf/certs/"},
            }
            if sql_setup is not None
            else None,
        )
        # Sometimes very bad things happen, this ensures that the container will
        # be cleaned up on process exit no matter what
        cleanup = mkcleanup(docker_client, container)
        try:
            # Get the IP from the docker daemon
            inspect = docker_client.api.inspect_container(container.id)
            container_ip = inspect["NetworkSettings"]["IPAddress"]
            # Create certificate
            ca_cert_path = pathlib.Path(cert_dir_path, "ca.pem")
            key_path = pathlib.Path(cert_dir_path, "server.key")
            subprocess.call(
                [
                    "openssl",
                    "req",
                    "-x509",
                    "-newkey",
                    "rsa:2048",
                    "-keyout",
                    key_path.resolve(),
                    "-out",
                    ca_cert_path.resolve(),
                    "-days",
                    "365",
                    "-nodes",
                    "-sha256",
                    "-subj",
                    f"/C=US/ST=Oregon/L=Portland/O=Feedface/OU=Org/CN={container_ip}",
                ]
            )
            ca_cert_path.chmod(0o664)
            key_path.chmod(0o660)
            pathlib.Path(cert_dir_path, "ready").write_text("ready")
            # Wait until MySQL reports it's ready for connections
            ready = False
            for line in container.logs(stream=True, follow=True):
                LOGGER.debug(
                    "MySQL log: %s", line.decode(errors="ignore").strip()
                )
                if b"ready for connections" in line:
                    ready = True
                    break
            if not ready:
                raise MySQLFailedToStart()
            # Ensure that we can make a connection
            while not check_connection(container_ip, DEFAULT_PORT):
                pass
            LOGGER.debug("MySQL running")
            # Yield IP of container to caller
            yield container_ip, ca_cert_path.resolve()
        finally:
            cleanup()
