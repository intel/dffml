from dffml.util.asynctestcase import AsyncTestCase

from aiohttp import web
from aiohttp import client
import aiohttp
import asyncio
import logging
import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


baseUrl = 'http://0.0.0.0:8888'
mountPoint = '/fakeUuid'

# From StackOverflow: https://stackoverflow.com/a/52403071
class ReverseProxyHandler(object):

    async def wsforward(ws_from,ws_to):
        async for msg in ws_from:
            logger.info('>>> msg: %s',pprint.pformat(msg))
            mt = msg.type
            md = msg.data
            if mt == aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(md)
            elif mt == aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(md)
            elif mt == aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif mt == aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            elif ws_to.closed:
                await ws_to.close(code=ws_to.close_code, message=msg.extra)
            else:
                raise ValueError('Unexpected message type: %s' % (msg,))

    async def __call__(self, req):
        proxyPath = req.match_info.get('proxyPath','no proxyPath placeholder defined')
        reqH = req.headers.copy()
        if reqH['connection'] == 'Upgrade' \
                and reqH['upgrade'] == 'websocket' and req.method == 'GET':

          ws_server = web.WebSocketResponse()
          await ws_server.prepare(req)
          logger.info('##### WS_SERVER %s' % pprint.pformat(ws_server))

          client_session = aiohttp.ClientSession(cookies=req.cookies)
          async with client_session.ws_connect(
            baseUrl+req.path_qs,
          },
          ) as ws_client:
            logger.info('##### WS_CLIENT %s' % pprint.pformat(ws_client))

            coro = asyncio.wait([
                    wsforward(ws_server,ws_client),
                    wsforward(ws_client,ws_server)
                ],
                return_when=asyncio.FIRST_COMPLETED)
            # TODO replace with
            # https://aiohttp.readthedocs.io/en/stable/web_advanced.html#background-tasks
            finished,unfinished = await coro

            return ws_server
        else:
          async with client.request(
              req.method,baseUrl+mountPoint+proxyPath,
              headers = reqH,
              allow_redirects=False,
              data = await req.read()
          ) as res:
              headers = res.headers.copy()
              body = await res.read()
              return web.Response(
                headers = headers,
                status = res.status,
                body = body
              )
          return ws_server

app = web.Application()
app.router.add_route('*',mountPoint + '{proxyPath:.*}', handler)
web.run_app(app,port=3984)

class TestReverseProxy(AsyncTestCase):

    async def test_run(self):
import asyncio
from aiohttp import web

async def handler(request):
    return web.Response(text="OK")


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    print("======= Serving on http://127.0.0.1:8080/ ======")

    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    await asyncio.sleep(100*3600)


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    pass
loop.close()
