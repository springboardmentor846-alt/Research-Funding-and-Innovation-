import os
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import httpx

from app.patents.providers.lens_client import LensClientConfig, LensPatentClient

load_dotenv(Path(r'd:\research-funding-platform-2\backend\.env'))

os.environ['PYTHONPATH'] = r'd:\research-funding-platform-2\backend'

async def main():
    token = (os.getenv('LENS_API_TOKEN') or '').strip()
    print('token present', bool(token))
    print('token len', len(token))
    print('base url', os.getenv('THE_LENS_BASE_URL', 'https://api.lens.org'))
    print('env file exists', Path(r'd:\research-funding-platform-2\backend\.env').exists())

    client = LensPatentClient(LensClientConfig(base_url='https://api.lens.org', token=token))
    try:
        result = await client.search(query='*', from_offset=0, size=1)
        print('records', len(result.records))
        print('total', result.total)
        if result.records:
            print('sample', json.dumps(result.records[0], default=str)[:1500])
        else:
            print('sample', 'none')
    finally:
        await client.aclose()

asyncio.run(main())
