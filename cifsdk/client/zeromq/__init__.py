import logging
from cifsdk.client.zeromq.base import Base
from cifsdk.client import Client

from cifsdk.zmq.msg import Msg
from csirtg_indicator import Indicator
from .constants import TRACE, FIREBALL_SIZE

logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)


class ZMQ(Client, Base):

    def _should_fireball(self, data):
        if self.fireball or len(data) > 25:
            return True

    def indicators_search(self, filters, decode=True):
        return self._send(Msg.INDICATORS_SEARCH, filters,
                          decode=decode)

    def _prepare_data(self, data):
        if isinstance(data, dict):
            data = self._kv_to_indicator(data)

        if type(data) == dict:
            data = [data]

        if isinstance(data, list) and isinstance(data[0], Indicator):
            data = [i.__dict__() for i in data]

        if isinstance(data, Indicator):
            data = [data.__dict__()]

        return data

    def indicators_create(self, data=[], nowait=False, fireball=False,
                          f_size=FIREBALL_SIZE):

        if isinstance(data, list) and len(data) == 0:
            return

        data = self._prepare_data(data)

        if fireball or self._should_fireball(data):
            return self._send_fireball(data, f_size)

        return self._send(Msg.INDICATORS_CREATE, data, nowait=nowait)

    def indicators_delete(self, data):
        if isinstance(data, dict):
            data = self._kv_to_indicator(data)

        if isinstance(data, Indicator):
            data = str(data)

        return self._send(Msg.INDICATORS_DELETE, data)
