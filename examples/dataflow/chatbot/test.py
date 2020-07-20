import random
import asyncio
import tempfile
from aiohttp import web
from unittest import mock
from http import HTTPStatus
from aiohttp.test_utils import TestServer

from dffml.util.asynctestcase import AsyncTestCase
from dffml import (
    DataFlow,
    run,
    opimp_in,
    INISecretConfig,
    INISecret,
    Input,
    BaseDataFlowFacilitatorObjectContext,
)

from .operations import *

OPERATIONS = [get_room_id, stream_chat, send_message, interpret_message]
BOT_NAME = "testbot"
MESSAGES = [
    "Hey",
    "train model",
    """
details:
model-type: scikitlr
model-name: randomModel
features: Years:int:1 Expertise:int:1 Trust:float:1
predict: Salary:float:1
data:
Years,Expertise,Trust,Salary
0,1,0.1,10
1,3,0.2,20
2,5,0.3,30
3,7,0.4,40
""",
    """
predict:
model-type: scikitlr
model-name: randomModel
features: Years:int:1 Expertise:int:1 Trust:float:1
predict: Salary:float:1
data:
Years,Expertise,Trust
6,13,0.7
""",
    "Haikyu",
]
MESSAGES = [f"@{BOT_NAME} " + msg for msg in MESSAGES]


class TestRoom:
    async def get_room_id(self, request):
        request = await request.json()
        try:
            if request["uri"] == self.uri:
                return web.json_response({"id": self.room_id})
        except:
            return web.json_response(
                {"error": "room uri does not match"},
                status=HTTPStatus.BAD_REQUEST,
            )

    async def receive_msg(self, request):
        try:
            request = await request.json()
            msg = request["text"]
            self.inbox.append(msg)
            return web.json_response(
                {"text": "received"}, status=HTTPStatus.OK,
            )
        except:
            return web.json_response(
                {"error": "room uri does not match"},
                status=HTTPStatus.BAD_REQUEST,
            )

    def __init__(self, uri):
        self.app = web.Application()
        self.uri = uri
        self.room_id = random.randint(1, 1000)
        self.inbox = []

        self.app.add_routes(
            [
                web.post("/rooms", self.get_room_id),
                web.post(
                    f"/rooms/{self.room_id}/chatMessages", self.receive_msg
                ),
            ]
        )


class FakeStreamChatImpContext(BaseDataFlowFacilitatorObjectContext):
    def __init__(self, *args, **kwargs):
        super().__init__()

    async def _run(self):
        for msg in MESSAGES:
            yield {"message": msg}
            await asyncio.sleep(0.1)

    async def run(self, *args, **kwargs):
        result = self._run()
        return result


class TestGitterBot(AsyncTestCase):
    async def setUp(self):
        self.room_name = "test_room/test"
        self.room = TestRoom(uri=self.room_name)
        self.server = TestServer(app=self.room.app, scheme="http")
        await self.server.start_server()

    async def tearDown(self):
        await self.server.close()

    async def test_dataflow(self):
        server_addr = f"http://127.0.0.1:{self.server.port}"
        with mock.patch.object(
            stream_chat.imp, "CONTEXT", new=FakeStreamChatImpContext
        ):
            with tempfile.NamedTemporaryFile(suffix=".ini") as config_file:
                config_file.write(b"[secrets]\n")
                config_file.write(b"access_token = 123\n")
                config_file.write(f"botname = {BOT_NAME}\n".encode())
                config_file.write(f"api_url = {server_addr}\n".encode())
                config_file.write(f"stream_url = {server_addr}\n".encode())
                config_file.seek(0)

                bot_config = GitterChannelConfig(
                    INISecret(filename=config_file.name)
                )
                dataflow = DataFlow(
                    operations={x.op.name: x for x in OPERATIONS},
                    implementations={x.op.name: x.imp for x in OPERATIONS},
                    configs={x.op.name: bot_config for x in OPERATIONS},
                )
                dataflow.seed = [
                    Input(
                        value=self.room_name,
                        definition=get_room_id.op.inputs["room_uri"],
                    )
                ]
                async for ctx, result in run(dataflow):
                    pass

            self.assertEqual(
                self.room.inbox,
                [
                    "Hey Hooman ฅ^•ﻌ•^ฅ",
                    "Gimme more details!!",
                    "Done!!",
                    "Salary: 70.00000000000001",
                    " Oops ,I didnt get that ᕙ(⇀‸↼‶)ᕗ ",
                ],
            )
