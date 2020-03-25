import logging

from cifsdk.client.http.base import Base
from cifsdk.client import Client
from csirtg_indicator import Indicator

from .utils import _check_data, _check_status
from pprint import pprint

from .constants import RETRIES_DELAY, TRACE, TIMEOUT, RETRIES

logger = logging.getLogger(__name__)


class HTTP(Client, Base):

    def indicators_search(self, filters):
        if isinstance(filters, list):
            return self._post('indicators', filters, 200)

        data = self._get('indicators', params=filters)
        return data

    def indicators_search_bulk(self, data):
        return self._post('indicators', data, 200)

    def indicators_create(self, data):
        if isinstance(data, Indicator):
            data = data.__dict__()

        if type(data) == dict:
            data = [data]

        if isinstance(data, list) and isinstance(data[0], Indicator):
            data = [i.__dict__() for i in data]

        rv = self._put('indicators', data)
        return rv["data"]

    def indicators_delete(self, filters):
        rv = self._delete('indicators', params=filters)
        return rv["data"]
