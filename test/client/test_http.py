import pytest
from cifsdk.client.http import HTTP as Client
import responses


@pytest.fixture
def client():
    yield Client(remote='http://localhost')


@responses.activate
def test_http(client):
    assert client.remote


@responses.activate
def test_http_search(client):
    responses.add(responses.GET, 'http://localhost/indicators',
                  json=[], status=200, headers={'Content-Length': '2'})

    rv = client.indicators_search({})
    assert rv == []

    responses.add(responses.POST, 'http://localhost/indicators',
                  json=[], status=200, headers={'Content-Length': '2'})

    rv = client.indicators_search([])
    assert rv == []


@responses.activate
def test_http_create(client):
    responses.add(responses.PUT, 'http://localhost/indicators',
                  json={'data': ''}, status=200)

    rv = client.indicators_create([{}])
    assert rv == ''


@responses.activate
def test_http_delete(client):
    responses.add(responses.DELETE, 'http://localhost/indicators',
                  json={'data': ''}, status=200)

    rv = client.indicators_delete({})
    assert rv == ''
