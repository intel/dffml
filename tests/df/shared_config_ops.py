from dffml import *

KEY = Definition(name="key", primitive="string")
VALUE = Definition(name="value", primitive="Any")
KEY_DONE = Definition(name="key_done", primitive="string")
VALUE_DONE = Definition(name="value_done", primitive="Any")


@config
class CheckSecretMatchConfig:
    secret: "BaseSecret"


@op(
    inputs={"key": KEY, "value": VALUE},
    outputs={"key_done": KEY_DONE},
    config_cls=CheckSecretMatchConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def mem_set(self, key, value):
    await self.sctx.set(key, value)
    return {"key_done": key}


@op(
    inputs={"key": KEY_DONE},
    outputs={"value": VALUE_DONE},
    config_cls=CheckSecretMatchConfig,
    imp_enter={"secret": lambda self: self.config.secret},
    ctx_enter={"sctx": lambda self: self.parent.secret()},
)
async def mem_get(self, key):
    value = await self.sctx.get(key)
    return {"value": value}
