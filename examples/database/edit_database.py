import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    response = await client.edit_database('database_id', name='new_name', memory=1024)


    print(response.status)  # "Success" if the database was edited successfully



asyncio.run(example())
