import io
import re
import sys
import json
import tempfile
import contextlib
from aiohttp import ClientSession, ClientTimeout

from dffml.cli.cli import CLI
from dffml import op, config, Definition, BaseSecret

ACCESSTOKEN = Definition(name="access_tok3n", primitive="str")
ROOMNAME = Definition(name="room_name", primitive="str")
ROOMID = Definition(name="room_id", primitive="str")
MESSAGE = Definition(name="message", primitive="str")
TOSEND = Definition(name="to_send", primitive="str")


@config
class GitterChannelConfig:
    secret: BaseSecret


@op(
    inputs={"room_uri": ROOMNAME},
    outputs={"room_id": ROOMID},
    config_cls=GitterChannelConfig,
    imp_enter={
        "secret": lambda self: self.config.secret,
        "session": lambda self: ClientSession(trust_env=True),
    },
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def get_room_id(self, room_uri):
    # Get unique roomid from room uri
    access_token = await self.sctx.get("access_token")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    api_url = await self.sctx.get("api_url")
    url = f"{api_url}/rooms"
    async with self.parent.session.post(
        url, json={"uri":room_uri}, headers=headers
    ) as resp:
        response = await resp.json()
        return {"room_id": response["id"]}


@op(
    inputs={"room_id": ROOMID},
    outputs={"message": MESSAGE},
    config_cls=GitterChannelConfig,
    imp_enter={
        "secret": lambda self: self.config.secret,
        "session": lambda self: ClientSession(
            trust_env=True, timeout=ClientTimeout(total=None)
        ),
    },
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def stream_chat(self, room_id):
    # Listen to messages in room
    access_token = await self.sctx.get("access_token")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    stream_url = await self.sctx.get("stream_url")

    url = f"{stream_url}/rooms/{room_id}/chatMessages"
    botname = await self.sctx.get("botname")

    async with self.parent.session.get(url, headers=headers) as resp:
        async for data in resp.content:
            # Gitter sends " \n" at some intervals
            if data == " \n".encode():
                continue
            print(f"\n\n Got data {data} \n\n")
            data = json.loads(data.strip())
            message = data["text"]
            # Only listen to messages directed to bot
            if f"@{botname}" not in message:
                continue
            yield {"message": message}


@op(
    inputs={"message": TOSEND, "room_id": ROOMID},
    config_cls=GitterChannelConfig,
    imp_enter={
        "secret": lambda self: self.config.secret,
        "session": lambda self: ClientSession(trust_env=True),
    },
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def send_message(self, message, room_id):
    access_token = await self.sctx.get("access_token")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    try:
        message = json.loads(message)
        message = json.dumps(message, indent=4, sort_keys=True)
    except:
        pass

    # For new line we need \\n,else Gitter api
    # responds with 'Bad Request'
    message = message.replace("\n", "\\n")
    api_url = await self.sctx.get("api_url")
    url = f"{api_url}/rooms/{room_id}/chatMessages"

    async with self.parent.session.post(
        url, headers=headers, json={"text": message}
    ) as resp:
        response = await resp.json()
        return


@op(
    inputs={"message": MESSAGE,},
    outputs={"message": TOSEND},
    config_cls=GitterChannelConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def interpret_message(self, message):
    greet = ["hey", "hello", "hi"]
    for x in greet:
        if x in message.lower():
            return {"message": "Hey Hooman ฅ^•ﻌ•^ฅ"}

    def extract_data(raw_data):
        raw_data = raw_data.split("data:")
        data = {"model-data": raw_data[1]}
        raw_data = raw_data[0].split("\n")
        for x in raw_data:
            k, *v = x.split(":")
            if isinstance(v, list):  # for features
                v = ":".join(v)
            k = k.strip()
            v = v.strip()
            if k:  # avoid blank
                data[k] = v
        return data

    # Removing username from message
    # The regex matches @ followed by anything that
    # is not a whitespace in the first group and
    # the rest of the string in the second group.
    # We replace the string by the second group.
    message = re.sub(r"(@[^\s]+)(.*)", r"\2", message).strip()

    if message.lower().startswith("train model"):
        return {"message": "Gimme more details!!"}

    elif message.lower().startswith("predict:"):
        # Only replace first occurence of predict
        # because the feature to predict will be labeled predict
        raw_data = message.replace("predict:", "", 1).strip()
        cmds = ["predict", "all"]

    elif message.lower().startswith("details:"):
        raw_data = message.replace("details:", "",).strip()
        cmds = ["train"]

    else:
        return {"message": " Oops ,I didnt get that ᕙ(⇀‸↼‶)ᕗ "}

    # If predict or train, extract data
    data = extract_data(raw_data)
    if "model-type" in data:
        model_type = data["model-type"]
    if "model-name" in data:
        model_name = data["model-name"]
    else:
        model_name = "mymodel"

    features = data["features"].split(" ")
    predict = data["predict"]
    model_data = data["model-data"]

    with tempfile.NamedTemporaryFile(suffix=".csv") as fileobj:
        fileobj.write(model_data.lstrip().encode())
        fileobj.seek(0)

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            preds = await CLI.cli(
                *cmds,
                "-model",
                model_type,
                "-model-directory",
                model_name,
                "-model-features",
                *features,
                "-model-predict",
                predict,
                "-sources",
                "f=csv",
                "-source-filename",
                fileobj.name,
            )
            sys.stdout.flush()

    if "train" in cmds:
        return {"message": "Done!!"}
    else:
        m = {}
        for pred in preds:
            pred = pred.predictions()
            m.update({p: pred[p]["value"] for p in pred})
        message = [f"{k}: {v}" for k, v in m.items()]
        message = "\n".join(message)
    return {"message": message}
