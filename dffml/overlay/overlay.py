from ..df.types import DataFlow
<<<<<<< Updated upstream
from ..util.entrypoint import base_entry_point
=======
from ..util.entrypoint import base_entry_point, Entrypoint


@dffml.op(
    expand=["result"],
)
def plugins_installed(plugin_base: Entrypoint) -> Any:
    # TODO Have a plugin which itself is used to discover plugin types. We can
    # then reference by string and load the base class for that plugin type.
    # This is really just a stub for that more advanced abitrary version.
    # >>> Plugin.load("dffml.model")
    # Model
    # Iterate over all the installed overlays
    return cls.load()


# TODO For inital overlay load of top level system context, we call
# plugins_installed to get all the dataflows which need to be merged. We then
# execute the merged installed overlays if LOAD_DEFAULT is given for
# ``overlay`` on ``run()``. Then we we run, the only default overlay added from
# the main package on install is one which defines an output operation which
# grabs all the dataflows within the input network of the running context for
# the overlay, merges them togther, and returns the to be run dataflow.
def dataflow_merge(merged: Dict[str, Any], dataflow: DataFlow) -> Dict[str, Any]:
    # The merged overlay dataflow
    merge(merged, dataflow.export(), list_append=True)


def dataflow_fromdict(merged: dict):
    # Export the overlay dataflow
    return DataFlow._fromdict(**merged)


    # TODO(alice) Figure out if there is something we need to do with
    # regards to the order in which overlays are applied. Can we use their
    # input allowlist to detect interdependencies? Do we need to?
    # The merged overlay dataflow
    merged: Dict[str, Any] = {}
    # Iterate over all the installed overlays
    for installed_overlay in cls.load():
        merge(merged, loaded.export(), list_append=True)
        # Export the overlay dataflow
        return DataFlow._fromdict(**merged)

    def apply(self):
    # TODO this should become an operation and then used as dataflow as
    # class style
    # TODO(security) Some method to audit if org overlays were taken into
    # account  within explicitly passed overlay
    async for ctx, results in run(
        overlay,
        [Input(value=dataflow, definition=DataFlow.DEFINITION)],
        orchestrator=orchestrator,
    ):
        pass
    # We require via manifest/did method style schema for output
    # probably, it should have an overlayed top level key of data schema
    # type matching system context within that an open architecutre
    # within that with a dataflow within that.
    return results["overlayed"]
>>>>>>> Stashed changes


@base_entry_point("dffml.overlay", "overlay")
class Overlay(DataFlow):
    @classmethod
    async def default(cls):
        # TODO(alice) Figure out if there is something we need to do with
        # regards to the order in which overlays are applied. Can we use their
        # input allowlist to detect interdependencies? Do we need to?
        # The merged overlay dataflow
        merged: Dict[str, Any] = {}
        # Iterate over all the installed overlays
        for installed_overlay in :
            merge(merged, loaded.export(), list_append=True)
            # Export the overlay dataflow
            return DataFlow._fromdict(**merged)

        cls.load()


    def apply(self):
        # TODO this should become an operation and then used as dataflow as
        # class style
        # TODO(security) Some method to audit if org overlays were taken into
        # account  within explicitly passed overlay
        async for ctx, results in run(
            overlay,
            [Input(value=dataflow, definition=DataFlow.DEFINITION)],
            orchestrator=orchestrator,
        ):
            pass
        # We require via manifest/did method style schema for output
        # probably, it should have an overlayed top level key of data schema
        # type matching system context within that an open architecutre
        # within that with a dataflow within that.
        return results["overlayed"]
