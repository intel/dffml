import os
import json
import time
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

DOCKER_IMAGE = "mongo:4"
# MongoDB daemons default listing port
DEFAULT_PORT = 27017
# Environment variables passed to MongoDB container
DOCKER_ENV = {
    "MONGO_INITDB_ROOT_USERNAME": "mongoadmin",
    "MONGO_INITDB_ROOT_PASSWORD": "secret",
}
DOCKER_NA: str = "Failed to connect to docker daemon"
DOCKER_AVAILABLE: bool = False
try:
    DOCKER_CLIENT: docker.DockerClient = docker.from_env()
    DOCKER_AVAILABLE = DOCKER_CLIENT.ping()
    DOCKER_CLIENT.close()
except:
    pass


class MongoDBFailedToStart(Exception):
    pass  # pragma: no cov


def check_connection(addr: str, port: int, *, timeout: float = 0.1) -> bool:
    """
    Attempt to make a TCP connection. Return if a connection was made in
    less than ``timeout`` seconds. Return True if a connection is made within
    the timeout.
    """
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
def mongodb(*, js_setup: Optional[str] = None):
    """
    Start a MongoDB container and yield the IP of the container once ready for
    connections. ``js_setup`` should be the .sql file used to initialize the
    database.
    """
    if not DOCKER_AVAILABLE:
        raise unittest.SkipTest("Need docker to run MongoDB")

    docker_client: docker.DockerClient = docker.from_env()
    with tempfile.TemporaryDirectory() as tempdir:
        # Volumes to mount
        volumes = {}
        # Dump out JavaScript initialization file
        if js_setup is not None:
            js_setup_path = pathlib.Path(tempdir, "dump.js")
            js_setup_path.write_text(js_setup)
            js_setup_path.chmod(0o555)
            volumes[js_setup_path.resolve()] = {
                "bind": "/docker-entrypoint-initdb.d/dump.js"
            }
        # Tell the docker daemon to start MongoDB
        LOGGER.debug("Starting MongoDB...")
        container = docker_client.containers.run(
            DOCKER_IMAGE,
            environment=DOCKER_ENV,
            detach=True,
            auto_remove=True,
            volumes=volumes,
        )
        # Sometimes very bad things happen, this ensures that the container will
        # be cleaned up on process exit no matter what
        cleanup = mkcleanup(docker_client, container)
        try:
            # Get the IP from the docker daemon
            inspect = docker_client.api.inspect_container(container.id)
            container_ip = inspect["NetworkSettings"]["IPAddress"]
            # Wait until MongoDB reports it's ready for connections
            container_start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            ready = False
            for line in container.logs(stream=True, follow=True):
                now_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
                LOGGER.debug(
                    "MongoDB log (%0.02f seconds): %s",
                    (now_time - container_start_time),
                    line.decode(errors="ignore").strip(),
                )
                if not line.startswith(b"{"):
                    continue
                log_entry = json.loads(line.decode())
                if (
                    log_entry["c"] == "NETWORK"
                    and log_entry["ctx"] == "listener"
                    and log_entry["msg"] == "Waiting for connections"
                ):
                    ready = True
                    break
            if not ready:
                raise MongoDBFailedToStart('Never saw "Waiting for connections"')
            # Ensure that we can make a connection
            start_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            max_timeout = float(os.getenv("MONGODB_START_TIMEOUT", "600"))
            LOGGER.debug(
                "Attempting to connect to MongoDB: Timeout of %d seconds", max_timeout,
            )
            while not check_connection(container_ip, DEFAULT_PORT):
                end_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
                if (end_time - start_time) >= max_timeout:
                    raise MongoDBFailedToStart("Timed out waiting for MongoDB")
            end_time = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            LOGGER.debug(
                "MongoDB running: Took %0.02f seconds", end_time - container_start_time,
            )
            # Yield IP of container to caller
            yield container_ip
        finally:
            cleanup()
