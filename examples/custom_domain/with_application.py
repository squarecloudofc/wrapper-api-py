import squarecloud as square

client = square.Client(api_key='API KEY')


async def example():
    app = await client.app('application_id')
    await app.set_custom_domain('my_custom_domain.example.br')
