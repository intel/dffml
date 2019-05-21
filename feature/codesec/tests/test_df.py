from dffml.df.types import Definition, \
                           Input
from dffml.df.linker import Linker
from dffml.df.base import op, \
                          opwraped_in, \
                          operation_in, \
                          opimp_in, \
                          BaseConfig, \
                          BaseRedundancyCheckerConfig, \
                          StringInputSetContext
from dffml.df.memory import MemoryInputNetwork, \
                            MemoryOperationNetwork, \
                            MemoryOperationNetworkConfig, \
                            MemoryLockNetwork, \
                            MemoryRedundancyChecker, \
                            MemoryKeyValueStore, \
                            MemoryOperationImplementationNetwork, \
                            MemoryOperationImplementationNetworkConfig, \
                            MemoryOrchestratorConfig, \
                            MemoryOrchestrator, \
                            MemoryInputSet, \
                            MemoryInputSetConfig

from dffml.operation.output import Associate
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_codesec.feature.operations import *

OPERATIONS = operation_in(sys.modules[__name__])
OPIMPS = opimp_in(sys.modules[__name__])

class TestRunner(AsyncTestCase):

    async def test_run(self):
        repos = [
            'http://pkg.freebsd.org/FreeBSD:13:amd64/latest/All/ImageMagick7-7.0.8.22_1.txz',
            'https://download.clearlinux.org/releases/10540/clear/x86_64/os/Packages/sudo-setuid-1.8.17p1-34.x86_64.rpm',
            'https://rpmfind.net/linux/fedora/linux/updates/29/Everything/x86_64/Packages/g/gzip-1.9-9.fc29.x86_64.rpm',
            'https://archives.fedoraproject.org/pub/archive/fedora/linux/releases/20/Everything/x86_64/os/Packages/c/curl-7.32.0-3.fc20.x86_64.rpm'
            ]

        # Orchestrate the running of these operations
        async with MemoryOrchestrator.basic_config(
                operations=OPERATIONS,
                opimps={imp.op.name: imp \
                  for imp in \
                  [Imp(BaseConfig()) for Imp in OPIMPS]}
                ) as orchestrator:

            definitions = Operation.definitions(*OPERATIONS)

            urls = [Input(value=URL,
                          definition=definitions['URL'],
                          parents=False) for URL in repos]

            associate_spec = Input(value=['rpm_filename', 'binary_is_PIE'],
                                   definition=definitions['associate_spec'],
                                   parents=False)

            async with orchestrator() as octx:
                # Add our inputs to the input network with the context being the URL
                for url in urls:
                    await octx.ictx.add(
                        MemoryInputSet(
                            MemoryInputSetConfig(
                                ctx=StringInputSetContext(url.value),
                                inputs=[url, associate_spec]
                            )
                        )
                    )
                async for ctx, results in octx.run_operations(strict=True):
                    self.assertTrue(results)
