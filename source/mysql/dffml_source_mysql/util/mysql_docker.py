import os
import atexit
import socket
import logging
import tempfile
from contextlib import contextmanager
from typing import Optional

import docker

LOGGER = logging.getLogger(__package__)

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
    Attempt to make a TCP connection. Return True if a connection was made in
    less than ``timeout`` seconds.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((addr, port))
            return True
    except:
        pass
    return False


def mkcleanup(docker_client, container, fileobj):
    """
    Create a function which will remove the temporary file and stop the
    container. The function will register itself with the :py:`atexit` module to
    ensure that the container is stopped before Python exits. It will unregister
    itself whenever it is called.
    """
    func = None

    def cleanup():
        atexit.unregister(func)
        if os.path.exists(fileobj.name):
            os.unlink(fileobj.name)
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
    with tempfile.NamedTemporaryFile(delete=False) as fileobj:
        # Dump out SQL query to file
        if sql_setup is not None:
            fileobj.write(sql_setup.encode())
            fileobj.seek(0)
            os.chmod(fileobj.name, 0o555)
        # Tell the docker daemon to start MySQL
        LOGGER.debug("Starting MySQL...")
        container = docker_client.containers.run(
            DOCKER_IMAGE,
            detach=True,
            auto_remove=True,
            volumes={
                os.path.abspath(fileobj.name): {
                    "bind": "/docker-entrypoint-initdb.d/dump.sql"
                }
            }
            if sql_setup is not None
            else None,
            environment=DOCKER_ENV,
        )
        # Sometimes very bad things happen, this ensures that the container will
        # be cleaned up on process exit no matter what
        cleanup = mkcleanup(docker_client, container, fileobj)
        try:
            # If the container exists the log stream will stop
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
            # Get the IP from the docker daemon
            inspect = docker_client.api.inspect_container(container.id)
            container_ip = inspect["NetworkSettings"]["IPAddress"]
            # Ensure that we can make a connection
            while not check_connection(container_ip, DEFAULT_PORT):
                pass
            LOGGER.debug("MySQL running")
            # Yield IP of container to caller
            yield container_ip
        finally:
            cleanup()
