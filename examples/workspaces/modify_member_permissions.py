import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    resp = await client.modify_member_permissions('WORKSPACE_ID', user_id='USER_ID', permissions='PERM')
    print('modify member permissions response:', resp.status)


asyncio.run(example())
