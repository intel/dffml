import os
import hashlib
import asyncio
import concurrent.futures
from typing import Dict, Any

from dffml.df.base import Definition
from dffml.df.types import Operation
from dffml.df.base import (
    OperationImplementationContext,
    OperationImplementation,
)

definitions = [
    Definition(name="MsgOut", primitive="string"),
    Definition(name="MsgIn", primitive="string"),
    Definition(name="TargetUser", primitive="string"),
    Definition(name="LoggedInUser", primitive="string"),
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)

@op({
    "inputs": {
    },
    "outputs": {
    })
async def 
