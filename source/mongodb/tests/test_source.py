import socket
import inspect
import contextlib
from unittest.mock import patch

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase

from dffml_source_mongodb.source import MongoDBSourceConfig, MongoDBSource

from dffml_source_mongodb.util.mongodb_docker import mongodb, DOCKER_ENV, DEFAULT_PORT


class TestMongoDBSource(AsyncTestCase, SourceTest):

    JS_SETUP = """"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.container_ip = cls.exit_stack.enter_context(mongodb())
        cls.source_config = MongoDBSourceConfig(
            uri=f'mongodb://{DOCKER_ENV["MONGO_INITDB_ROOT_USERNAME"]}:{DOCKER_ENV["MONGO_INITDB_ROOT_PASSWORD"]}@mongodb.unittest:{DEFAULT_PORT}/',
            db="mydb",
            collection="mycollection",
        )
        # Make it so that when the client tries to connect to mongodb.unittest the
        # address it gets back is the one for the container
        cls.exit_stack.enter_context(
            patch(
                "socket.getaddrinfo",
                return_value=[
                    (
                        socket.AF_INET,
                        socket.SOCK_STREAM,
                        6,
                        "",
                        (cls.container_ip, DEFAULT_PORT),
                    )
                ],
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    async def setUpSource(self):
        return MongoDBSource(self.source_config)
