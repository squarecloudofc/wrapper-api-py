import asyncio

import squarecloud as square

client = square.Client('API_KEY')


async def example() -> None:
    app = await client.app('application_id')

    # See that since no request was made, the cache is empty
    print(app.cache.status)  # None
    print(app.cache.logs)  # None
    print(app.cache.snapshot)  # None

    # Now, lets make some requests
    await app.status()
    await app.logs()
    await app.snapshot()

    # Now the cache is updated
    print(app.cache.status)  # StatusData(...)
    print(app.cache.logs)  # LogsData(...)
    print(app.cache.snapshot)  # SnapshotData(...)


asyncio.run(example())
