import asyncio

import squarecloud as square

client = square.Client(api_key='API KEY')


async def example() -> None:
    snapshot = await client.snapshot('application_id')
    print(snapshot.url)


asyncio.run(example())
