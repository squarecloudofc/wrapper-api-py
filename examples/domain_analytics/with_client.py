import squarecloud as square

client = square.Client(api_key='API KEY')


async def example():
    analytics = await client.last_deploys('application_id')
    print(analytics)  # DomainAnalytics(...)
