from http import HTTPStatus
from contextlib import asynccontextmanager

from dffml.df.base import BaseConfig
from dffml.util.asynctestcase import AsyncTestCase

from aiohttp import web
from aiohttp import client
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import aiohttp
import asyncio
import logging
import pprint

from dffml.log import LOGGER

import logging
logging.basicConfig(level=logging.DEBUG)

# From StackOverflow: https://stackoverflow.com/a/52403071
class ReverseProxyHandlerContext(object):

    def __init__(self,
                 parent: 'ReverseProxyHandler',
                 *,
                 address: str = '127.0.0.1',
                 port: int = 0) -> None:
        self.parent = parent
        self.address = address
        self.port = port
        self.upstream = {}
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    async def wsforward(self, ws_from, ws_to):
        async for msg in ws_from:
            self.logger.info('>>> msg: %s',pprint.pformat(msg))
            if msg.type == aiohttp.WSMsgType.TEXT:
                await ws_to.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                await ws_to.send_bytes(msg.data)
            elif msg.type == aiohttp.WSMsgType.PING:
                await ws_to.ping()
            elif msg.type == aiohttp.WSMsgType.PONG:
                await ws_to.pong()
            elif ws_to.closed:
                await ws_to.close(code=ws_to.close_code, message=msg.extra)
            else:
                raise ValueError('Unexpected message type: %s' % (msg,))

    async def handler_proxy(self, req):
        self.logger.debug('%s', pprint.pformat(req))
        proxyPath = req.match_info.get('proxyPath','no proxyPath placeholder defined')
        reqH = req.headers.copy()
        if reqH['connection'] == 'Upgrade' \
                and reqH['upgrade'] == 'websocket' and req.method == 'GET':

          ws_server = web.WebSocketResponse()
          await ws_server.prepare(req)
          self.logger.info('##### WS_SERVER %s' % pprint.pformat(ws_server))

          client_session = aiohttp.ClientSession(cookies=req.cookies)
          async with client_session.ws_connect(
            baseUrl+req.path_qs,
          ) as ws_client:
            self.logger.info('##### WS_CLIENT %s' % pprint.pformat(ws_client))

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

    async def add_upstream(self,
                           address: str,
                           port: int,
                           subdomain: str = None,
                           path: str = None):
        self.upstream[(subdomain, path,)] = (address, port,)

    async def __aenter__(self) -> 'ReverseProxyHandlerContext':
        self.app = web.Application()
        self.app.router.add_resource('').add_route('*',
                                                    self.handler_proxy)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.address, self.port)
        await self.site.start()
        self.address, self.port = self.site._server.sockets[0].getsockname()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.site.stop()
        await self.runner.cleanup()

class ReverseProxyHandler(object):

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def __call__(self, address='127.0.0.1', port=0) -> 'ReverseProxyHandlerContext':
        return ReverseProxyHandlerContext(self, address=address, port=port)

@asynccontextmanager
async def rproxy(self, subdomain, path):
    rproxyh = ReverseProxyHandler(BaseConfig())
    async with rproxyh() as ctx:
        await ctx.add_upstream(address=self.server.host,
                               port=self.server.port,
                               subdomain='test',
                               path='/route/this')
        yield ctx

class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        async def hello(request):
            return web.Response(text='Hello, world')

        app = web.Application()
        app.router.add_get('/', hello)
        return app

    @unittest_run_loop
    async def test_example(self):
        subdomain = 'test'
        path = '/route/this'
        async with rproxy(self, subdomain=subdomain, path=path) as rctx, \
                aiohttp.ClientSession() as session:
            address = 'localhost'
            port = rctx.port
            url = 'http://%s.%s:%d%s' % (subdomain, address, port, path,)
            LOGGER.debug('rproxy url: %s', url)
            async with session.get(url) as resp:
                self.assertEqual(resp.status, HTTPStatus.OK)
                text = await resp.text()
                self.assertEqual('Hello, world', text)
