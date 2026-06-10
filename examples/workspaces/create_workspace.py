import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    workspace = await client.create_workspace('WORKSPACE_NAME')
    print('created workspace:', workspace.to_dict())


asyncio.run(example())
