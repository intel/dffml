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
            tty=True,
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
            # Wait until MySQL reports it's ready for connections
            container_start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            ready = False
            for line in container.logs(stream=True, follow=True):
                now_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
                LOGGER.debug(
                    "HADOOP log (%0.02f seconds): %s",
                    (now_time - container_start_time),
                    line.decode(errors="ignore").strip(),
                )
                if b"Starting Solr server daemon:[  OK  ]" in line:
                    ready = True
                    break
            if not ready:
                raise HadoopFailedToStart('Never saw "Starting Solr server daemon:[  OK  ]"')
            # Ensure that we can make a connection
            end_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            LOGGER.debug(
                "Hadoop running: Took %0.02f seconds",
                end_time - container_start_time,
            )
            # Yield IP of container to caller
            yield container_ip
        finally:
            LOGGER.debug("HADOOP shutting down...")
            cleanup()
