import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    resp = await client.delete_workspace('WORKSPACE_ID')
    print('delete workspace response:', resp.status)


asyncio.run(example())
