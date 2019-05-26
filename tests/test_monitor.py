# SPDX-License-Identifier: MIT
# Copyright (c) 2019 Intel Corporation
import asyncio
import unittest

from dffml.util.monitor import Monitor, Task
from dffml.util.asynctestcase import AsyncTestCase


async def test_task(task=Task()):
    for i in range(0, 10):
        await asyncio.sleep(0.01)
        await task.update(i)


async def log_task(task=Task()):
    for i in range(0, 10):
        await task.log("i is now %d", i)


async def recv_statuses(status, sleep):
    log = []
    await asyncio.sleep(sleep)
    async for msg in status:
        log.append(msg)
    return log


class TestMonitor(AsyncTestCase):
    def setUp(self):
        self.monitor = Monitor()

    async def test_00_await_complete(self):
        await self.monitor.complete((await self.monitor.start(test_task)).key)

    async def test_01_single_watching_status(self):
        task = await self.monitor.start(test_task)
        statuses = await recv_statuses(self.monitor.status(task.key), 0.05)
        self.assertEqual(len(statuses), 10)
        for i in range(0, 10):
            self.assertEqual(statuses[i], i)

    async def test_02_multiple_watching(self):
        task = await self.monitor.start(test_task)
        res = await asyncio.gather(
            *[
                recv_statuses(self.monitor.status(task.key), i * 0.01)
                for i in range(0, 5)
            ]
        )
        for statuses in res:
            self.assertEqual(len(statuses), 10)
            for i in range(0, 10):
                self.assertEqual(statuses[i], i)

    async def test_03_log(self):
        await self.monitor.complete((await self.monitor.start(log_task)).key)

    async def test_04_already_complete(self):
        task = await self.monitor.start(log_task)
        await self.monitor.complete(task.key)
        await self.monitor.complete(task.key)

    async def test_05_already_complete_status(self):
        task = await self.monitor.start(log_task)
        await self.monitor.complete(task.key)
        self.assertFalse([msg async for msg in self.monitor.status(task.key)])

    async def test_06_log_status(self):
        i = 0
        async for msg in self.monitor.log_status(
            (await self.monitor.start(test_task)).key
        ):
            self.assertEqual(msg, i)
            i += 1
        self.assertEqual(i, 10)

    async def test_07_already_running(self):
        task = await self.monitor.start(test_task)
        await self.monitor.start(task, task.key)
        await self.monitor.complete(task.key)
