import asyncio

import squarecloud as square

client = square.Client(api_key='API_KEY')


async def example() -> None:
    # Get workspace
    fetched = await client.get_workspace('WORKSPACE_ID')
    print('fetched workspace:', fetched.to_dict())


asyncio.run(example())
