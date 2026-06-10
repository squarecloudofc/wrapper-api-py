import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    new_password = await client.reset_database_password('database_id')
    print(new_password) # The String contains the new database password

    await asyncio.sleep(3)

    response = await client.reset_database_certificate('database_id')
    print(response.status) # “Success” if the database certificate was successfully reset



asyncio.run(example())
