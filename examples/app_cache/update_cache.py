import asyncio

import squarecloud as square

client = square.Client('API_KEY')


async def example() -> None:
    app = await client.app('application_id')

    status = await app.status()
    logs = await app.logs()
    snapshot = await app.snapshot()

    app.cache.clear()  # Clear cache

    app.cache.update(status, logs, snapshot)  # Update cache

    print(app.cache.status)  # StatusData(...)
    print(app.cache.logs)  # LogsData(...)
    print(app.cache.snapshot)  # SnapshotData(...)


asyncio.run(example())
