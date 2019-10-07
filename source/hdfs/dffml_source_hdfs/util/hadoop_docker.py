import os
import ssl
import time
import shutil
import atexit
import socket
import pathlib
import logging
import tempfile
import unittest
import subprocess
from contextlib import contextmanager
from typing import Optional

import docker

LOGGER = logging.getLogger(__package__)

logging.basicConfig(level=logging.DEBUG)

DOCKER_IMAGE = "cloudera/quickstart:latest"
# MySQL daemons default listing port
# DEFAULT_PORT = 3306
# Environment variables passed to MySQL container
# DOCKER_ENV = {
#     "MYSQL_DATABASE": "db",
#     "MYSQL_USER": "user",
#     "MYSQL_PASSWORD": "pass",
#     "MYSQL_RANDOM_ROOT_PASSWORD": "yes",
# }
# # MySQL server config file
# MY_CONF = """[mysqld]
# ssl-ca=/conf/certs/ca.pem
# ssl-cert=/conf/certs/server-cert.pem
# ssl-key=/conf/certs/server-key.pem
# """
DOCKER_NA: str = "Failed to connect to docker daemon"
DOCKER_AVAILABLE: bool = False

DOCKER_CLIENT: docker.DockerClient = docker.from_env()
print("DOCKERRRR CLIENNNTTT")
print(DOCKER_CLIENT)

DOCKER_AVAILABLE = DOCKER_CLIENT.ping()
print("DOCKERRRR AVAILABLE")
print(DOCKER_CLIENT)
DOCKER_CLIENT.close()

print("EXCEPTION PASSED")
    


class HadoopFailedToStart(Exception):
    pass  # pragma: no cov


def check_connection(addr: str, port: int, *, timeout: float = 0.1) -> bool:
    """
    Attempt to make a TCP connection. Return if a connection was made in
    less than ``timeout`` seconds. Return True if a connection is made within
    the timeout.
    """
    print("CCHECKKK CONNECITON")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(float(timeout))
        try:
            s.connect((addr, port))
        except Exception as error:
            return False
    return True


def mkcleanup(docker_client, container):
    """
    Create a function which will remove the temporary file and stop the
    container. The function will register itself with the :py:`atexit` module to
    ensure that the container is stopped before Python exits. It will unregister
    itself whenever it is called.
    """
    print("CHECKKK CONNECITON mkcleanup")

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
def hadoop():
    """
    Start a MySQL container and yield the IP of the container once ready for
    connections. ``sql_setup`` should be the .sql file used to initialize the
    database.
    """
    print("CHECK CONNECITON HADOOP")

    if not DOCKER_AVAILABLE:
        raise unittest.SkipTest("Need docker to run Hadoop")

    docker_client: docker.DockerClient = docker.from_env()
    print("\n\n Docker client retrieved")
    with tempfile.TemporaryDirectory() as tempdir:
        # Create server config
        # sql_conf_path = pathlib.Path(tempdir, "my.conf")
        # sql_conf_path.write_text(MY_CONF)
        # sql_conf_path.chmod(0o660)
        # Create cert folder
        # cert_dir_path = pathlib.Path(tempdir, "certs")
        # cert_dir_path.mkdir(mode=0o755)
        # Dump out SQL query to file
        # if sql_setup is not None:
        #     sql_setup_path = pathlib.Path(tempdir, "sample_data.csv")
        #     sql_setup_path.write_text(sql_setup)
        #     sql_setup_path.chmod(0o555)
        # Tell the docker daemon to start MySQL
        LOGGER.debug("Starting Hadoop...")
        # os.system("bash")
        container = docker_client.containers.run(
            DOCKER_IMAGE,
            command="/usr/bin/docker-quickstart",
            # environment=DOCKER_ENV,
            hostname="quickstart.cloudera",
            privileged=True,
            detach=True,
            auto_remove=True,
            # ports={
            # 8888:8888,
            # 7180:7180,
            # 80:80,
            # 50070:50070,
            # 8020:8020,
            # },
            
        )

        print("\n\n\n DOCKERR RUN DONE")

        # Sometimes very bad things happen, this ensures that the container will
        # be cleaned up on process exit no matter what
        cleanup = mkcleanup(docker_client, container)
        try:
            # Get the IP from the docker daemon
            inspect = docker_client.api.inspect_container(container.id)
            container_ip = inspect["NetworkSettings"]["IPAddress"]
            # Create certificate
            # From: https://mariadb.com/kb/en/library/certificate-creation-with-openssl/
            cmds = [
                ["openssl", "genrsa", "-out", "ca-key.pem", "2048"],
                [
                    "openssl",
                    "req",
                    "-new",
                    "-x509",
                    "-nodes",
                    "-key",
                    "ca-key.pem",
                    "-out",
                    "ca.pem",
                    "-subj",
                    f"/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Root Cert/CN=mysql.unittest",
                ],
                [
                    "openssl",
                    "req",
                    "-newkey",
                    "rsa:2048",
                    "-nodes",
                    "-keyout",
                    "server-key.pem",
                    "-out",
                    "server-req.pem",
                    "-subj",
                    f"/C=US/ST=Oregon/L=Portland/O=Company Name/OU=Server Cert/CN=mysql.unittest",
                ],
                [
                    "openssl",
                    "rsa",
                    "-in",
                    "server-key.pem",
                    "-out",
                    "server-key.pem",
                ],
                [
                    "openssl",
                    "x509",
                    "-req",
                    "-in",
                    "server-req.pem",
                    "-days",
                    "1",
                    "-CA",
                    "ca.pem",
                    "-CAkey",
                    "ca-key.pem",
                    "-set_serial",
                    "01",
                    "-out",
                    "server-cert.pem",
                ],
            ]
            for cmd in cmds:
                subprocess.call(cmd, cwd=cert_dir_path.resolve())
            root_cert_path = pathlib.Path(cert_dir_path, "ca.pem")
            server_cert_path = pathlib.Path(cert_dir_path, "server-cert.pem")
            server_key_path = pathlib.Path(cert_dir_path, "server-key.pem")
            server_cert_path.chmod(0o660)
            server_key_path.chmod(0o660)
            pathlib.Path(cert_dir_path, "ready").write_text("ready")
            # Wait until MySQL reports it's ready for connections
            container_start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            ready = 0
            for line in container.logs(stream=True, follow=True):
                now_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
                LOGGER.debug(
                    "HADOOP log (%0.02f seconds): %s",
                    (now_time - container_start_time),
                    line.decode(errors="ignore").strip(),
                )
                if b"ready for connections" in line:
                    ready += 1
                if ready == 2:
                    break
            if ready != 2:
                raise HadoopFailedToStart('Never saw "ready for connections"')
            # Ensure that we can make a connection
            start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            max_timeout = float(os.getenv("HADOOP_START_TIMEOUT", "600"))
            LOGGER.debug(
                "Attempting to connect to Hadoop: Timeout of %d seconds",
                max_timeout,
            )
            while not check_connection(container_ip, DEFAULT_PORT):
                end_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
                if (end_time - start_time) >= max_timeout:
                    raise HadoopFailedToStart("Timed out waiting for Hadoop")
            end_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            LOGGER.debug(
                "Hadoop running: Took %0.02f seconds",
                end_time - container_start_time,
            )
            # Yield IP of container to caller
            yield container_ip, root_cert_path.resolve()
        finally:
            cleanup()
