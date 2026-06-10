import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    resp = await client.remove_member_from_workspace('WORKSPACE_ID', user_id='USER_ID')
    print('remove member response:', resp.status)


asyncio.run(example())
