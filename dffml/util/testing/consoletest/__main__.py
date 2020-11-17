import sys
import asyncio

from .cli import main

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
