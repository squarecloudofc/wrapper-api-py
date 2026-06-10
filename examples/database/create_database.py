import asyncio

import squarecloud as square

client = square.Client(api_key='your_api_key')


async def example() -> None:
    database = await client.create_database(
        name="database_name",
        memory=1024, # Memory in MB,
        type="mongo", # "mongo", "redis", "postgres" or "mysql"
        version="8.0.11" # Optional parameter to specify the database version. if it is not passed, it will be inferred automatically 
    )


    print(database.id) # Database ID
    print(database.name) # Database name
    print(database.type) # Database type
    print(database.cluster) # Database cluster
    print(database.memory) # Amount of memory allocated to the database in MB   
    print(database.certificate) # Database certificate in Base64 format. You can save in PEM File.
    print(database.password) # Database password.
    print(database.connection_url) # Database connection URL.
    print(database.cpu) # Amount of VCpu allocated to the database

    database.certificate.save()
    database.certificate.save(filename="private-key", export_to="key")
    database.certificate.save(dir="certs-teste", filename='certift', export_to="cert")
   

asyncio.run(example())
