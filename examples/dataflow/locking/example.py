import asyncio
from dffml import Definition, DataFlow, Input, op
from dffml.noasync import run

OBJ = Definition(name="obj", primitive="mapping")
LOCKED_OBJ = Definition(name="locked_obj", primitive="mapping", lock=True)
SLEEP_TIME = Definition(name="sleep_time", primitive="int")
INTEGER = Definition(name="integer", primitive="int")


@op(inputs={"obj": OBJ, "sleep_for": SLEEP_TIME, "i": INTEGER})
async def run_me(obj: dict, sleep_for: int, i: int) -> None:
    obj["i"] = i
    await asyncio.sleep(sleep_for)
    print(f"set i = {i}, got i = {obj['i']}")


print("Running dataflow without locked object")
for ctx, result in run(
    DataFlow(run_me),
    [
        Input(value={}, definition=OBJ),
        Input(value=0.1, definition=SLEEP_TIME),
        Input(value=0.2, definition=SLEEP_TIME),
        Input(value=1, definition=INTEGER),
        Input(value=2, definition=INTEGER),
    ],
):
    pass

print("Running dataflow with locked object")
run_me.op = run_me.op._replace(
    inputs={"obj": LOCKED_OBJ, "sleep_for": SLEEP_TIME, "i": INTEGER}
)
for ctx, result in run(
    DataFlow(run_me),
    [
        Input(value={}, definition=LOCKED_OBJ),
        Input(value=0.1, definition=SLEEP_TIME),
        Input(value=0.2, definition=SLEEP_TIME),
        Input(value=1, definition=INTEGER),
        Input(value=2, definition=INTEGER),
    ],
):
    pass
