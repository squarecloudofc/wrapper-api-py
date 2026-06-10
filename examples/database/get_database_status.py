import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    database_status = await client.get_database_status('database_id')

    print(database_status.ram)  # '70MB'
    print(database_status.cpu)  # '5%'
    print(database_status.network)  # {'total': '0 KB ↑ 0 KB ↓', 'now': '0 KB ↑ 0 KB ↓'}
    print(database_status.running)  # True | False
    print(database_status.storage)  # '0MB'
    print(database_status.status)  # 'running'
    print(database_status.uptime) # 1772118587831 (timestemp)


asyncio.run(example())
