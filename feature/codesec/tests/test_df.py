import json

from dffml.df import *
from dffml.operation.output import Associate
from dffml_feature_codesec.feature.operations import *

from dffml.util.asynctestcase import AsyncTestCase

OPWRAPED = opwraped_in(sys.modules[__name__])
OPERATIONS = operation_in(sys.modules[__name__]) + \
             list(map(lambda item: item.op, OPWRAPED))
OPIMPS = opimp_in(sys.modules[__name__]) + \
         list(map(lambda item: item.imp, OPWRAPED))

class TestRunner(AsyncTestCase):

    async def test_run(self):
        linker = Linker()
        exported = linker.export(*OPERATIONS)
        definitions, operations, _outputs = linker.resolve(exported)

        repos = [
            'http://pkg.freebsd.org/FreeBSD:13:amd64/latest/All/ImageMagick7-7.0.8.22_1.txz',
            # 'https://download.clearlinux.org/releases/10540/clear/x86_64/os/Packages/sudo-setuid-1.8.17p1-34.x86_64.rpm',
            # 'https://rpmfind.net/linux/fedora/linux/updates/29/Everything/x86_64/Packages/g/gzip-1.9-9.fc29.x86_64.rpm',
            # 'https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/20/Everything/x86_64/os/Packages/c/curl-7.32.0-3.fc20.x86_64.rpm'
            ]
        urls = [Input(value=URL,
                      definition=definitions['URL'],
                      parents=False) for URL in repos]

        associate_spec = Input(value=['rpm_filename', 'binary_is_PIE'],
                               definition=definitions['associate_spec'],
                               parents=False)

        opimps = {imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}

        dff = DataFlowFacilitator(
            input_network = MemoryInputNetwork(BaseConfig()),
            operation_network = MemoryOperationNetwork(
                MemoryOperationNetworkConfig(
                    operations=list(operations.values())
                )
            ),
            lock_network = MemoryLockNetwork(BaseConfig()),
            rchecker = MemoryRedundancyChecker(
                BaseRedundancyCheckerConfig(
                    key_value_store=MemoryKeyValueStore(BaseConfig())
                )
            ),
            opimp_network = MemoryOperationImplementationNetwork(
                MemoryOperationImplementationNetworkConfig(
                    operations=opimps
                )
            ),
            orchestrator = MemoryOrchestrator(BaseConfig())
        )


        # Orchestrate the running of these operations
        async with dff as dff:
            async with dff() as dffctx:
                # Add our inputs to the input network with the context being the URL
                for url in urls:
                    await dffctx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(url.value),
                                inputs=[url, associate_spec]
                            )
                        )
                    )
                async for ctx, results in dffctx.evaluate():
                    print()
                    print((await ctx.handle()).as_string(),
                          json.dumps(results, sort_keys=True,
                                     indent=4, separators=(',', ':')))
                    print()
                    # self.assertTrue(results)
