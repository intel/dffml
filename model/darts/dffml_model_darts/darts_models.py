import os
import sys
import pathlib

from darts.models import ExponentialSmoothing


from dffml.base import field
from dffml.util.config.numpy import make_config_numpy
from dffml.util.entrypoint import entrypoint
from dffml.feature.feature import Feature, Features
from dffml_model_darts.darts_base import (
    Darts,
    DartsContext,
)

for entry_pont_name, name, cls in [
    (
        "dartsexponentialsmoothing",
        "ExponentialSmoothing",
        ExponentialSmoothing,
    ),
]:

    config_fields = dict()
    parentContext = DartsContext
    parentModel = Darts
    config_fields["predict"] = (
        Feature,
        field("Label or the value to be predicted"),
    )

    dffml_config_properties = {
        **{
            "directory": (
                pathlib.Path,
                field("Directory where state should be saved",),
            ),
            "features": (Features, field("Features to train on")),
        },
        **config_fields,
    }

    dffml_config = make_config_numpy(
        name + "ModelConfig", cls, properties=dffml_config_properties
    )

    dffml_cls_ctx = type(name + "ModelContext", (parentContext,), {},)

    dffml_cls = type(
        name + "Model",
        (parentModel,),
        {
            "CONFIG": dffml_config,
            "CONTEXT": dffml_cls_ctx,
            "DARTS_MODEL": cls,
        },
    )
    # Add the ENTRY_POINT_ORIG_LABEL
    dffml_cls = entrypoint(entry_point_name)(dffml_cls)

    setattr(sys.modules[__name__], dffml_config.__qualname__, dffml_config)
    setattr(sys.modules[__name__], dffml_cls_ctx.__qualname__, dffml_cls_ctx)
    setattr(sys.modules[__name__], dffml_cls.__qualname__, dffml_cls)
