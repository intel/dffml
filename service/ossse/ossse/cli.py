'''
Command line interface evaluates packages given their source URLs
'''
import os
import re
import glob
import json
import asyncio
import pathlib
import datetime
import traceback
import pkg_resources
from functools import partial
from typing import Union

import motor.motor_asyncio
from aiohttp import web, WSMsgType

import dffml
# TODO, is this still here?
# from dffml.util.monitor import Monitor, Task

from cvemap.cvedb import CVEDB, Client
from cvemap.cvemap import CVEMap

from .log import LOGGER

LOGGER = LOGGER.getChild('cli')

class DB(object):

    def __init__(self, uri=os.environ.get("DATABASE_CONNECTION_STRING", 'mongodb://localhost:27017')):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.conn = self.client['wl']['items']

    async def total(self):
        return await self.conn.count_documents({})

    async def page(self, page_size, page_num):
        skips = page_size * (page_num - 1)
        cursor = self.conn.find()
        if skips > 0:
            cursor.skip(skips)
        cursor.limit(page_size)
        async for document in cursor:
            yield document


@dffml.config
class DBImportConfig:
    sources: dffml.Sources = dffml.field(
        "Sources to import from into mongodb",
    )


class DBImport(dffml.CMD):
    CONFIG = DBImportConfig

    async def run(self):
        self.db = DB()
        async for record in dffml.load(self.sources):
            valid = dffml.export(record.features())
            if 'features' in valid \
                    and 'crypto' in valid['features'] \
                    and 'evidence' in valid['features']['crypto']:
                del valid['features']['crypto']['evidence']
            valid['_id'] = valid['src_url']
            await self.db.conn.insert_one(valid)


@dffml.config
class EvaluationServerConfig:
    port: int = dffml.field(
        'Port to bind to',
        default=5000,
    )
    addr: str = dffml.field(
        'Address to bind to',
        default='127.0.0.1',
    )
    sources: dffml.Sources = dffml.field(
        "Sources to import from into mongodb",
        default=dffml.Sources(),
    )


class EvaluationServer(dffml.CMD):
    CONFIG = EvaluationServerConfig

    def asset_path(self, *args):
        return pkg_resources.resource_filename(__name__,
                os.path.join('html', *args))

    async def configure(self):
        self.assets_path = self.asset_path('dist')

    async def sync(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        task = request.app.loop.create_task(self.sync_sub(request, ws))
        try:
            async for msg in ws:
                if msg.type == WSMsgType.CLOSE:
                    await ws.close()
                elif msg.type != WSMsgType.TEXT:
                    continue
                LOGGER.debug('Got ws message: %r', msg.data)
                try:
                    data = msg.json()
                except Exception as error:
                    LOGGER.warning('JSON decode error: %r: %s', msg, error)
                    continue
                try:
                    request.app.loop.create_task(self.sync_pub(request, ws,
                        **data))
                except Exception as error:
                    LOGGER.warning('sync_pub error: %r: %s: %s', msg, error,
                            traceback.format_exc())
                    continue
        finally:
            task.cancel()
        return ws

    async def sync_pub(self, request, ws, *, method: str = '', name: str = '',
            value = None, meta = None, **kwargs):
        if meta is None:
            meta = {}
        if method == 'get':
            getter = getattr(self, 'sync_get_%s' % (meta.get('__type', ''),),
                    self.sync_get)
            await getter(request, ws, name, meta)
        elif method == 'set' and not value is None:
            setter = getattr(self, 'sync_set_%s' % (meta.get('__type', ''),),
                    self.sync_set)
            await setter(request, ws, name, value, meta)

    async def sync_get_record(self, request, ws, name, meta):
        # Dataflow as class / Metrics as running output operations over cached flow or
        # wait until fulfiled
        record = await request.app['sources'].record(name)
        # if record.features():
        #     await ws.send_json(dict(name=name,  method='got', data=record.export()))
        #     return
        key, task, started = await self.evaluate_start(request.app, name)
        async for event, msg in task.events():
            if event == 'set':
                await ws.send_json(dict(name='%s.log' % (name,),  method='got',
                    data=msg))
            else:
                await ws.send_json({'event': event, 'msg': msg})
        results = await self.evaluate_finish(request.app, key, task, started)
        record.evaluated(results)
        await ws.send_json(dict(name=name,  method='got', data=record.export()))

    async def sync_get(self, request, ws, name, meta):
        pass

    async def sync_set(self, request, ws, name, data, meta):
        pass

    async def sync_sub(self, request, ws):
        # await ws.send_json({'event': event, 'msg': msg})
        pass

    async def index(self, request):
        with open(self.asset_path('dist', 'index.html')) as fd:
            return web.Response(text=fd.read(), content_type='text/html')

    async def setup(self, **kwargs):
        await self.configure()
        if not 'monitor' in kwargs:
            kwargs['monitor'] = dffml.Monitor()
        self.app = web.Application()
        # http://docs.aiohttp.org/en/stable/faq.html#where-do-i-put-my-database-connection-so-handlers-can-access-it
        self.app.update(kwargs)
        self.app.add_routes([
            web.get('/', self.index),
            web.get('/sync/', self.sync),
            ])
        self.app.router.add_static('/', self.assets_path)
        self.runner = web.AppRunner(self.app, access_log=None)
        await self.runner.setup()

    async def start(self):
        site = web.TCPSite(self.runner, self.addr, self.port)
        await site.start()
        LOGGER.info('Serving on %s:%d', self.addr, self.port)

    async def run(self):
        '''
        Binds to port and starts HTTP server
        '''
        async with self.sources as sources:
            await self.setup(features=features, sources=sources)
            await self.start()
            while True:
                await asyncio.sleep(60)

    async def _evaluate(self, app, key, task = None):
        # This class is the basic flow with no database caching
        # return await app['features'].evaluate(key, task=task)
        # Run the collection dataflow
        # TODO This is very similar to the HTTP API, in fact it's the first
        # iteration.
        # The Task stuff was kind of like the dataflow context stuff

        # Gross, hardcoded inputs and definitions.
        # TODO Convert this service to make it run via dataflows run
        # from the HTTP service once the HTTP service is refactored.
        async for ctx, results in dffml.run(
            self.dataflow,
            [
                dffml.Input(
                    value=key,
                    definition=self.dataflow.definitions["URL"],
                ),
                dffml.Input(
                    # "$(date +'%Y-%m-%d %H:%M')=quarter_start_date" \
                    value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    definition=self.dataflow.definitions["quarter_start_date"],
                ),

            ],
        ):
            # TODO Add events and publish changes to clients via data.set as we
            # iterate over data moving between operations here and run output
            # operations as soon as their dependency trees are satisified.
            if task is not None:
                for key, value in results.items():
                    await task.data.set(key, value)
            return results

    async def evaluate_start(self, app, key):
        task = await app['monitor'].task(key)
        if not task is None:
            return key, task, False
        data = await app['monitor'].start(partial(self._evaluate, app, key),
                key=key)
        return key, data, True

    async def evaluate_finish(self, app, key, data, started):
        results = await data.complete()
        if not started:
            return results
        await app['sources'].update(Record(key, data={'features': results}))
        return results

    async def evaluate(self, app, key):
        return await self.evaluate_finish(app,
                *(await self.evaluate_start(app, key)))


DEFAULT_ADMIN_SOURCE = dffml.JSONSource(
    filename=pathlib.Path(
        ".tools",
        "open-architecture",
        "shouldi",
        "server",
        "sources",
        "admin.json",
    ),
    readwrite=True,
    allowempty=True,
)


import dffml_feature_git.feature.operations


DATAFLOW = dffml.DataFlow(
    dffml.GroupBy,
    dffml_feature_git.feature.operations.make_quarters,
    dffml_feature_git.feature.operations.quarters_back_to_date,
    dffml_feature_git.feature.operations.check_if_valid_git_repository_URL,
    dffml_feature_git.feature.operations.clone_git_repo,
    dffml_feature_git.feature.operations.git_repo_default_branch,
    dffml_feature_git.feature.operations.git_repo_commit_from_date,
    dffml_feature_git.feature.operations.git_repo_author_lines_for_dates,
    dffml_feature_git.feature.operations.work,
    dffml_feature_git.feature.operations.git_commits,
    dffml_feature_git.feature.operations.count_authors,
    dffml_feature_git.feature.operations.cleanup_git_repo,
)
DATAFLOW.seed = [
    dffml.Input(
        value=10,
        definition=DATAFLOW.definitions['quarters'],
    ),
    dffml.Input(
        value=True,
        definition=DATAFLOW.definitions['no_git_branch_given'],
    ),
    dffml.Input(
        value={
            "authors": {
                "group": "author_count",
                "by": "quarter",
            },
            "commits": {
                "group": "commit_count",
                "by": "quarter",
            },
            "work": {
                "group": "work_spread",
                "by": "quarter",
            },
        },
        definition=DATAFLOW.definitions['group_by_spec'],
    ),
]


@dffml.config
class ServerConfig(EvaluationServerConfig):
    dataflow: Union[str, dffml.DataFlow] = dffml.field(
        "File containing exported DataFlow or dataflow itself",
        default=DATAFLOW,
    )
    admin: dffml.Sources = dffml.field(
        "Admin sources",
        default=dffml.Sources(DEFAULT_ADMIN_SOURCE),
    )
    configloader: dffml.BaseConfigLoader = dffml.field(
        "ConfigLoader to use for importing DataFlow", default=None,
    )


class Server(EvaluationServer):
    CONFIG = ServerConfig

    async def run(self):
        '''
        Binds to port and starts HTTP server
        cvedb_server = os.getenv('CVEDB', default=None)
        if not cvedb_server is None:
            self.cvemap = CVEMap(Client(server=cvedb_server))
        else:
            self.cvemap = CVEMap(CVEDB())
        '''
        self.db = DB()
        # Create directories for default source if not exists
        if self.admin and self.admin[0] is DEFAULT_ADMIN_SOURCE:
            if not self.admin[0].config.filename.parent.is_dir():
                self.admin[0].config.filename.parent.mkdir(parents=True)
        # We removed metrics in favor of features in favor of dataflows
        # We need to update to calling dataflows.
        # There was previously a Monitor for Monitoring execution of metrics
        # We might want to re-apply that to our dataflow context watching.
        async with self.sources as sources, self.admin as admin:
            # Have to match new double context entry
            async with sources() as sctx, admin() as actx:
                await self.setup(sources=sctx,
                        admin=actx,
                        db=self.db)
                await self.start()
                while True:
                    await asyncio.sleep(60)

    async def hasaccess(self, request, name, meta):
        # TODO
        return True

    async def sync_get_admin(self, request, ws, name, meta):
        if not await self.hasaccess(request, name, meta):
            return
        record = await request.app['admin'].record(name)
        record = record.export()
        data = record.get('features', {})
        data.update(record.get('extra', {}))
        if data:
            await ws.send_json(dict(name=name,  method='got', data=data,
                type='admin'))

    async def sync_set_admin(self, request, ws, name, value, meta):
        if not await self.hasaccess(request, name, meta):
            return
        record = await request.app['admin'].record(name)
        record.evaluated(value)
        await request.app['admin'].update(record)

    async def sync_get_cves(self, request, ws, name, meta):
        return
        async for cveid, cve in request.app['cvemap'].cves(name):
            await ws.send_json(dict(name=name,  method='got', data={cveid: cve},
                type='cves'))

    async def sync_get_total(self, request, ws, name, meta):
        await ws.send_json(dict(name=name,  method='got',
            data=await request.app['db'].total(), type='total'))

    async def sync_get_list(self, request, ws, name, meta):
        async for document in request.app['db'].page(
                meta.get('page_size', 5), meta.get('page_num', 0)):
            await ws.send_json(dict(name=name,  method='got', data=document,
                type='list'))

    async def sync_get_record(self, request, ws, name, meta):
        record = await request.app['sources'].record(name)
        if record.data.prediction:
            await ws.send_json(dict(name=name,  method='got', data=record.export(),
                type='record'))
            return
        key, task, started = await self.evaluate_start(request.app, name)
        async for event, msg in task.events():
            if event == 'set':
                await ws.send_json(dict(name=name, method='got', data=msg,
                    type='log'))
            elif event != 'done':
                await ws.send_json({'event': event, 'msg': msg})
        record = await self.evaluate_finish(request.app, key, task, started)
        await ws.send_json(dict(name=name,  method='got', data=record.export(),
                type='record'))

    async def sync_set(self, request, ws, name, data, meta):
        if not await self.hasaccess(request, name, meta):
            return

    async def _evaluate(self, app, key, task = None):
        # Grab any existing data
        record = await app['sources'].record(key)
        # Run the collection dataflow
        results = await super()._evaluate(app, key, task=task)
        # Update the results in the DB
        record.evaluated(results)
        await app['sources'].update(record)
        return record
        # Models were previously called prophets
        async for record, cl, cf in app['model'].predict(record.asyncgen(),
                app['features'], app['classifications']):
            # Predicted took classification and confidence in classification
            # Think it's still the same, Hashim has an open PR I believe
            record.predicted(cl, cf)
        return record

    async def evaluate_finish(self, app, key, data, started):
        record = await data.complete()
        if not started:
            return record
        await app['sources'].update(record)
        return record

    async def __aenter__(self):
        await super().__aenter__()
        if not isinstance(self.dataflow, dffml.DataFlow):
            dataflow_path = pathlib.Path(self.dataflow)
            config_cls = self.configloader
            if config_cls is None:
                config_type = dataflow_path.suffix.replace(".", "")
                config_cls = dffml.BaseConfigLoader.load(config_type)
            async with config_cls.withconfig(
                self.extra_config
            ) as configloader:
                async with configloader() as loader:
                    exported = await loader.loadb(dataflow_path.read_bytes())
                    self.dataflow = dffml.DataFlow._fromdict(**exported)
        return self

class OSSSECLI(dffml.CMD):
    '''
    CLI interface for wllearn expands upon dffml
    '''

    server = Server
    _import = DBImport
