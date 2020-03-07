

from csirtg_indicator import Indicator
from cifsdk.client.http import HTTP as Client


def search(filters={}):
    if len(filters) == 0:
        filters = {
            'itype': 'ipv4',
            'tags': 'botnet'
        }

    return Client().search(filters)


def create(**kv):
    i = Indicator(**kv)

    return Client().indicators_create(i)
