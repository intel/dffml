from ..df.types import DataFlow, Input
from ..operation.output import GetMultiDataFlowsMerged


DFFML_MAIN_PACKAGE_OVERLAY = DataFlow(
    # TODO In non default overlays, apply overlay to each operation, after or
    # before prioritization, or both, could be even different overlays.
    # TODO Use overlays to apply prioritizers to operations.
    GetMultiDataFlowsMerged,
    seed=[
        Input(
            value={"definition": DATAFLOW, "output_key": "overlayed"},
            definition=GetMultiDataFlowsMerged.op.spec,
        )
    ],
)
