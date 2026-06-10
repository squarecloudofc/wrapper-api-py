import asyncio

import squarecloud as square

client = square.Client(api_key="your_api_key")

async def example() -> None:
    response = await client.delete_database('database_id')


    print(response.status)  # "Success" if the database was deleted successfully

asyncio.run(example())
