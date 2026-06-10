import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    response = await client.get_database_certificate('database_id')

    response.save()
    response.save(export_to="key")
    response.save(export_to="cert")



asyncio.run(example())
