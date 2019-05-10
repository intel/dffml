import io
import os
import sys
import hashlib
import asyncio
import concurrent.futures
from typing import Dict, Any, NamedTuple

from dffml.df import op, Stage, Operation, OperationImplementation, \
    OperationImplementationContext

from dffml_feature_git.util.proc import check_output

# pylint: disable=no-name-in-module
from .definitions import UnhashedPassword, \
                         ScryptPassword

from .log import LOGGER

scrypt = Operation(
    name='scrypt',
    inputs={
        'password': UnhashedPassword,
    },
    outputs={
        'password': ScryptPassword
    },
    conditions=[])

class ScryptContext(OperationImplementationContext):

    @staticmethod
    def hash_password(password):
        # ---- BEGIN Python hashlib docs ----

        # The function provides scrypt password-based key derivation function as
        # defined in RFC 7914.

        # password and salt must be bytes-like objects. Applications and
        # libraries should limit password to a sensible length (e.g. 1024). salt
        # should be about 16 or more bytes from a proper source, e.g.
        # os.urandom().

        # n is the CPU/Memory cost factor, r the block size, p parallelization
        # factor and maxmem limits memory (OpenSSL 1.1.0 defaults to 32 MiB).
        # dklen is the length of the derived key.

        # ---- END Python hashlib docs ----

        # ---- BEGIN RFC 7914 (August 2016) 2. scrypt Parameters ----

        # The scrypt function takes several parameters.  The passphrase P is
        # typically a human-chosen password.  The salt is normally uniquely and
        # randomly generated [RFC4086].  The parameter r ("blockSize")
        # specifies the block size.  The CPU/Memory cost parameter N
        # ("costParameter") must be larger than 1, a power of 2, and less than
        # 2^(128 * r / 8).  The parallelization parameter p
        # ("parallelizationParameter") is a positive integer less than or equal
        # to ((2^32-1) * 32) / (128 * r).  The intended output length dkLen is
        # the length in octets of the key to be derived ("keyLength"); it is a
        # positive integer less than or equal to (2^32 - 1) * 32.

        # Users of scrypt can tune the parameters N, r, and p according to the
        # amount of memory and computing power available, the latency-bandwidth
        # product of the memory subsystem, and the amount of parallelism
        # desired.  At the current time, r=8 and p=1 appears to yield good
        # results, but as memory latency and CPU parallelism increase, it is
        # likely that the optimum values for both r and p will increase.  Note
        # also that since the computations of SMix are independent, a large
        # value of p can be used to increase the computational cost of scrypt
        # without increasing the memory usage; so we can expect scrypt to
        # remain useful even if the growth rates of CPU power and memory
        # capacity diverge.

        # ---- END RFC 7914 ----

        password = password.encode('utf-8')

        salt = os.urandom(16 * 4)
        n = 2 ** 10
        # 7 Is a lucky number, clearly a powerful choice
        r = 2 ** 7
        p = 1

        hashed_password = hashlib.scrypt(password, salt=salt, n=n, r=r, p=p)

        hashed_password = hashed_password.hex()
        salt = salt.hex()

        return hashed_password, salt

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # TODO raise error if longer than 1024 (validation should be done before
        # we submit to the thread pool. Weird behavior can happen if we raise in
        # there.
        hashed_password, salt = await self.parent.loop.run_in_executor(
                self.parent.pool, self.hash_password, inputs['password'])
        return {
            'password': {
                'hashed': hashed_password,
                'salt': salt,
                }
            }

class Scrypt(OperationImplementation):

    op = scrypt

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = None
        self.pool = None
        self.__pool = None

    def __call__(self,
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') \
            -> ScryptContext:
        return ScryptContext(self, ctx, ictx)

    async def __aenter__(self) -> 'OperationImplementationContext':
        self.loop = asyncio.get_event_loop()
        # ProcessPoolExecutor is slightly faster but deprecated and will be
        # removed in 3.9
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.__pool = self.pool.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__pool.__exit__(exc_type, exc_value, traceback)
        self.__pool = None
        self.pool = None
        self.loop = None
