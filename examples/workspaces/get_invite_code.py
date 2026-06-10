import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    code = await client.get_invite_code()
    print('invite code:', code)


asyncio.run(example())
