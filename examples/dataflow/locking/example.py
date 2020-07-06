import asyncio
from dffml import Definition, DataFlow, Input, op, run

OBJ = Definition(name="obj", primitive="Any")
LOCKED_OBJ = Definition(name="locked_obj", primitive="Any", lock=True)
SLEEP_TIME = Definition(name="sleep_time", primitive="int")
INTEGER = Definition(name="intefer", primitive="int")

TEST_OUT = []


class TestObj:
    def __init__(self):
        self.i = -1


@op(inputs={"obj": OBJ, "sleep_for": SLEEP_TIME, "i": INTEGER})
async def run_me(obj, sleep_for, i) -> None:
    obj.i = i
    await asyncio.sleep(sleep_for)
    s = f"set i = {i}, got i = {obj.i}"
    print(s)
    TEST_OUT.append([i, obj.i])


async def main():
    dataflow = DataFlow(
        operations={"run1": run_me.op, "run2": run_me.op},
        implementations={run_me.op.name: run_me.imp},
    )

    print("Running dataflow without locked object")
    obj = TestObj()
    dataflow.seed = [
        Input(value=obj, definition=OBJ),
        Input(value=0.2, definition=SLEEP_TIME),
        Input(value=2, definition=INTEGER),
        Input(value=1, definition=INTEGER),
    ]
    async for ctx, result in run(dataflow):
        pass

    print("Running dataflow with locked object")
    run_me.op = run_me.op._replace(
        inputs={"obj": LOCKED_OBJ, "sleep_for": SLEEP_TIME, "i": INTEGER}
    )
    dataflow = DataFlow(
        operations={"run1": run_me.op, "run2": run_me.op},
        implementations={run_me.op.name: run_me.imp},
    )
    obj = TestObj()
    dataflow.seed = [
        Input(value=obj, definition=LOCKED_OBJ),
        Input(value=0.2, definition=SLEEP_TIME),
        Input(value=2, definition=INTEGER),
        Input(value=1, definition=INTEGER),
    ]
    async for ctx, result in run(dataflow):
        pass

    for x in TEST_OUT[4:]:
        assert x[0] == x[1]


asyncio.run(main())
