import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    database_info = await client.get_database_info('database_id')


    print(database_info.id)  # Database ID
    print(database_info.name)  # Database name
    print(database_info.type)  # Database type ("redis", "mongodb", "mysql", "postgresql")
    print(database_info.cluster)  # Database cluster
    print(database_info.ram)  # Ram usage of the database in MB
    print(database_info.port)  # Database port
    print(database_info.created_at) # Database creation date in ISO 8601 format



asyncio.run(example())
