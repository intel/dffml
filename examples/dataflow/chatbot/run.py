import sys
import asyncio

from operations import *
from dffml import (
    DataFlow,
    run,
    operation_in,
    opimp_in,
    INISecretConfig,
    INISecret,
    Input,
)

OPERATIONS = [get_room_id, stream_chat, send_message, interpret_message]


async def main():
    bot_config = GitterChannelConfig(INISecret(filename="configs.ini"))
    dataflow = DataFlow(
        operations={x.op.name: x for x in OPERATIONS},
        implementations={x.op.name: x.imp for x in OPERATIONS},
        configs={x.op.name: bot_config for x in OPERATIONS},
    )
    room_name = "test_community1/community"
    dataflow.seed = [
        Input(value=room_name, definition=get_room_id.op.inputs["room_uri"])
    ]
    async for ctx, result in run(dataflow):
        pass


if __name__ == "__main__":
    asyncio.run(main())
