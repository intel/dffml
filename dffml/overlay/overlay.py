from ..df.types import DataFlow
from ..util.entrypoint import base_entry_point


@base_entry_point("dffml.overlay", "overlay")
class Overlay(DataFlow):
    @classmethod
    def default(cls):
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
