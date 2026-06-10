import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    all_ws = await client.all_workspaces()
    print('all workspaces:', all_ws)


asyncio.run(example())
