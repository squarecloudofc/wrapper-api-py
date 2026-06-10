import asyncio

from squarecloud import Client

client = Client(api_key="your_api_key")


async def main():
    app_id = ""
    all_snapshts = await client.all_app_snapshots(app_id)
    snapshot = all_snapshts[0]

    response = await client.restore_snapshot(
        application_type="app",  # "database" or "app"
        app_id=app_id,  # application id or database id
        snapshot_id=snapshot.name,  # snapshot id
        version_id=snapshot.version_id # snapshot version id
    )

    print(response.status)  # "success" or "error"

asyncio.run(main())