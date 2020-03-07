from cifsdk.client.dummy import Dummy as Client


def test_dummy():
    cli = Client('https://localhost:3000')
    assert cli.remote == 'https://localhost:3000'

    data = {
        'indicator': 'example.com',
        'tags': ['botnet']
    }
    assert cli.indicators_create(data)

    assert cli.indicators_search(data)
