# Data Flow Facilitator

## Operation Implementations

### Context Management

Database connections or sessions should be bought up or down within the
`OperationImplementation`. Taking the `conn` object on say a `sqlite` connection
would be done in the `OperationImplementationContext`.

Here's an example of creating a `aiohttp` Client Session for use within the
`run` method of an `OperationImplementationContext`.

> From [feature/codesec](../feature/codesec/dffml_feature_codesec/feature/operations.py)

```python
url_to_urlbytes = Operation(
    name='url_to_urlbytes',
    inputs={
        'URL': URL,
    },
    outputs={
        'download': URLBytes
    },
    conditions=[])

class URLBytesObject(NamedTuple):
    URL: str
    body: bytes

    def __repr__(self):
        return '%s(URL=%s, body=%s...)' % (self.__class__.__qualname__,
                                           self.URL, self.body[:10],)

class URLToURLBytesContext(OperationImplementationContext):

    async def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        async with self.parent.session.get(inputs['URL']) as resp:
            return {
                'download': URLBytesObject(URL=inputs['URL'],
                                           body=await resp.read())
            }

class URLToURLBytes(OperationImplementation):

    op = url_to_urlbytes

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self.session = None

    def __call__(self,
                 ctx: 'BaseInputSetContext',
                 ictx: 'BaseInputNetworkContext') \
            -> URLToURLBytesContext:
        return URLToURLBytesContext(self, ctx, ictx)

    async def __aenter__(self) -> 'OperationImplementationContext':
        self.client = aiohttp.ClientSession(trust_env=True)
        self.session = await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.__aexit__(exc_type, exc_value, traceback)
        self.client = None
        self.session = None
```

### CPU Bound Operations (Threading)

Since DFFML is written to make use of Python's `asyncio` module, all operations
run in the main thread unless explicitly scheduled to another thread.

> From [feature/auth](../feature/auth/dffml_feature_auth/feature/operations.py)

```python
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
        salt = os.urandom(16 * 4)
        hashed_password = hashlib.scrypt(password, salt=salt, n=n, r=r, p=p)
        return hashed_password.hex(), salt.hex()

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
        self.pool = concurrent.futures.ThreadPoolExecutor()
        self.__pool = self.pool.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__pool.__exit__(exc_type, exc_value, traceback)
        self.__pool = None
        self.pool = None
        self.loop = None
```
