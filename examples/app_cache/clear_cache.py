import asyncio

import squarecloud as square

client = square.Client('API_KEY')


async def example() -> None:
    app = await client.app('application_id')

    await app.status()
    await app.logs()
    await app.snapshot()

    print(app.cache.status)  # StatusData(...)
    print(app.cache.logs)  # LogsData(...)
    print(app.cache.snapshot)  # SnapshotData(...)

    app.cache.clear()  # Clear cache

    print(app.cache.status)  # None
    print(app.cache.logs)  # None
    print(app.cache.snapshot)  # None


asyncio.run(example())
