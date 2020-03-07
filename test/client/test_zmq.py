import pytest


from cifsdk.client.zeromq import ZMQ as Client

@pytest.fixture
def client():
    yield Client()


def test_zmq(client):
    assert client.remote


def test_zmq_create(client):
    def _send(*args, **kwargs):
        return []

    client._send = _send

    rv = client.indicators_create(['asdfasdf'])
    assert rv == []


def test_zmq_search(client):
    def _send(*args, **kwargs):
        return []

    client._send = _send

    rv = client.indicators_search(['asdfasdf'])
    assert rv == []


def test_zmq_delete(client):
    def _send(*args, **kwargs):
        return []

    client._send = _send

    rv = client.indicators_delete(['asdfasdf'])
    assert rv == []
