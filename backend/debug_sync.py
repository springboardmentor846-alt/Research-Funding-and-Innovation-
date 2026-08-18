import asyncio
import os

os.chdir('d:/research-funding-platform-2/backend')

from app.funding_intel.services.sync import SyncEngine


async def main() -> None:
    result = await SyncEngine().run(provider='nih', mode='incremental', force=True)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
