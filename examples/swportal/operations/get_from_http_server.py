"""
This is an example operation of how one might query an API to get the status of
a project's indicator. We use the httptest module to start an example API
server.
"""
import random

import aiohttp
import httptest
from dffml import op, Definition

from .definitions import UUID


class ExampleAPIServer(httptest.Handler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(random.choice(["PASS", "FAIL"]).encode())


@httptest.Server(ExampleAPIServer)
async def make_request_to_example_server(session, ts=httptest.NoServer()):
    async with session.get(ts.url()) as resp:
        return (await resp.read()).decode()


@op(
    inputs={"uuid": UUID},
    outputs={"result": Definition(name="api_result", primitive="string")},
    imp_enter={
        "session": (lambda self: aiohttp.ClientSession(trust_env=True))
    },
)
async def query_an_api(self, uuid: str, ts=httptest.NoServer()) -> str:
    return {
        "result": await make_request_to_example_server(self.parent.session)
    }
