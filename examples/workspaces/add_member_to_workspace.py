import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    resp = await client.add_member_to_workspace('WORKSPACE_ID', invite_code='INVITE_CODE', permissions='PERM')
    print('add member response:', resp.status)


asyncio.run(example())
