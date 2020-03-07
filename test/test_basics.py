import cifsdk
from cifsdk.client.http import HTTP as Client
from cifsdk.actor import Actor


def test_basics():
    c = Client()

    Actor()