import os
import atexit
import docker
import socket
import logging
import tempfile

from dffml.util.asynctestcase import AsyncTestCase

LOGGER = logging.getLogger(__package__)

logging.basicConfig(level=logging.DEBUG)

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
except:
    pass


class DockerTestCase:

    _container_ip = "127.0.0.1"

    @property
    def container_ip(self):
        return self._container_ip

    @classmethod
    def setUpClass(cls):
        cls.fileobj = tempfile.NamedTemporaryFile(delete=False)
        cls.fileobj.write(cls.SQL_SETUP.encode())
        cls.fileobj.seek(0)
        os.environ.update(DOCKER_ENV)
        if cls.mysql_already_running():
            return
        # Just in case something goes wrong and tearDownClass doesn't get called
        atexit.register(cls.tearDownClass)
        LOGGER.debug("Starting MySQL...")
        cls._container = DOCKER_CLIENT.containers.run(
            "mysql:8.0",
            detach=True,
            auto_remove=True,
            volumes={
                os.path.abspath(cls.fileobj.name): {
                    "bind": "/docker-entrypoint-initdb.d/dump.sql"
                }
            },
            environment=DOCKER_ENV,
        )
        try:
            inspect = DOCKER_CLIENT.api.inspect_container(cls._container.id)
            # If the container exists the log stream will stop
            ready = 0
            for line in cls._container.logs(stream=True, follow=True):
                LOGGER.debug(
                    "MySQL log: %s", line.decode(errors="ignore").strip()
                )
                if b"ready for connections" in line:
                    ready += 1
                if ready == 2:
                    break
            if ready != 2:
                raise Exception("Failed to start MySQL server")
            cls._container_ip = inspect["NetworkSettings"]["IPAddress"]
            while not cls.mysql_already_running():
                pass
            LOGGER.debug("MySQL running")
        except:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.fileobj.name):
            os.unlink(cls.fileobj.name)
        try:
            cls._container.stop()
            cls._container.wait()
        except:
            pass

    @classmethod
    def mysql_already_running(cls) -> bool:
        """
        True if we can connect to a local MySQL server
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((cls._container_ip, 3306))
                s.close()
                return True
        except:
            pass
        return False
