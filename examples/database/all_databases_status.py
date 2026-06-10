import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    
    all_status = await client.all_databases_status()



    for status in all_status:
        print(status.id) # The ID of the database.
        print(status.cpu) # The current CPU usage percentage.
        print(status.ram) # The current RAM usage
        print(status.running) # The boolean value if is running.



asyncio.run(example())
