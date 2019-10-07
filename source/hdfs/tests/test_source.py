import os
import json
import random
import socket
import unittest
import subprocess
import contextlib


from dffml_source_hdfs.source import HDFSSourceConfig, HDFSSource

from dffml.util.testing.source import SourceTest
from dffml.util.asynctestcase import AsyncTestCase
from dffml.source.csv import CSVSource, CSVSourceConfig

from dffml_source_hdfs.util.hadoop_docker import hadoop


class TestHDFSSource(SourceTest, AsyncTestCase):
    
    @classmethod
    def fake_socket_getaddrinfo(
        cls, host, port, family=0, type=0, proto=0, flags=0
    ):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (cls.container_ip, port))
        ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._exit_stack = contextlib.ExitStack()
        cls.exit_stack = cls._exit_stack.__enter__()
        cls.container_ip = cls.exit_stack.enter_context(
            hadoop()
        )
        cls.source_config = HDFSSourceConfig(
                host="localhost",
                port="50070",
                user="root",
                source=CSVSource(CSVSourceConfig(filename="sample_data.csv")),
                filepath="./home/dffml-source/sample_data.csv",
            )
        os.system("bash")
        cls.exit_stack.enter_context(
            patch(
                "socket.getaddrinfo",
                new=cls.fake_socket_getaddrinfo
            )
        )
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._exit_stack.__exit__(None, None, None)

    async def setUpSource(self):
        return HDFSSource(self.source_config)


    @unittest.skip("Labels not implemented")
    async def test_label(self):
        """
        Labels not implemented
        """

