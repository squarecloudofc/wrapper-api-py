import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    resp = await client.leave_workspace('WORKSPACE ID')
    print('leave workspace response:', resp.status)


asyncio.run(example())
