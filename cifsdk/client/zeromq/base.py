from json import loads
import logging
from tornado import ioloop
from zmq.eventloop.zmqstream import ZMQStream

try:
    from snappy import decompress, UncompressError

except ImportError:
    print("Requires google snappy compression library")
    raise SystemExit

try:
    import zmq

except ImportError:
    print("Requires pyzmq")
    raise SystemExit

from cifsdk.zmq.socket import Context
from cifsdk.constants import REMOTE
from cifsdk.zmq.msg import Msg
from .constants import TRACE, RCVTIMEO, SNDTIMEO, LINGER

logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)

basestring = (str, bytes)


class Base(object):

    def __init__(self, **kwargs):
        self.context = Context()
        self.socket = self.context.socket(zmq.REQ)
        self.nowait = kwargs.get('nowait', False)
        if self.nowait:
            self.socket = self.context.socket(zmq.DEALER)

        self.socket.RCVTIMEO = RCVTIMEO
        self.socket.SNDTIMEO = SNDTIMEO
        self.socket.LINGER = LINGER

        self.autoclose = kwargs.get('autoclose', False)

        self.remote = kwargs.get('remote', REMOTE)

        self.fireball = kwargs.get('fireball', False)

        self.loop = kwargs.get('loop')
        self.is_connected = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        # do our best to clean up potentially leaky FDs
        if hasattr(self, 'stream') and not self.stream.closed():
            self.stream.close()

        if hasattr(self, 'loop') and self.loop is not None:
            try:
                self.loop.close()
            except KeyError:
                pass

        self.socket.close()
        self.context.term()

    def _handle_message_fireball(self, m):
        logger.debug('message received')

        m = self._check_recv(loads(Msg.from_frame(m).data))

        self.response.append(m)

        self.num_responses -= 1
        logger.debug('num responses remaining: %i' % self.num_responses)

        if self.num_responses == 0:
            logger.debug('finishing up...')
            self.loop.stop()

    def _fireball_timeout(self):
        logger.info('fireball timeout')
        self.loop.stop()

    def _send_fireball(self, data, f_size):
        if len(data) == 0:
            logger.error('no data to send')
            return []

        self.loop = ioloop.IOLoop()
        self.socket.close()

        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.remote)

        self.stream = ZMQStream(self.socket, io_loop=self.loop)
        self.stream.on_recv(self._handle_message_fireball)

        self.stream.io_loop.call_later(SNDTIMEO, self._fireball_timeout)

        self.response = []

        if not isinstance(data, list):
            data = [data]

        self.num_responses = int((len(data) / f_size))
        if (len(data) % f_size) != 0:
            self.num_responses += 1

        logger.debug('responses expected: %i' % self.num_responses)

        batch = []
        for d in data:
            batch.append(d)
            if len(batch) == f_size:
                self.socket.send_msg(
                    Msg(mtype=Msg.INDICATORS_CREATE, data=batch)
                )
                batch = []

        if len(batch):
            self.socket.send_msg(Msg(mtype=Msg.INDICATORS_CREATE, data=batch))

        logger.debug("starting loop to receive")
        self.loop.start()

        # clean up FDs
        self.loop.close()
        self.stream.close()
        self.socket.close()
        return self.response

    @staticmethod
    def _check_recv(data):
        if data.get('message') == 'unauthorized':
            raise PermissionError

        if data.get('message') == 'busy':
            raise ConnectionRefusedError('System Busy')

        if data.get('message') == 'invalid search':
            raise TypeError('invalid search')

        if data.get('status') != 'success':
            raise RuntimeError(data.get('message'))

        if data.get('data') is None:
            raise RuntimeError('invalid response')

        return data

    def _recv(self, decode=True, close=True):
        m = self.socket.recv_msg()

        if close:
            self.socket.close()

        if not decode:
            return m.data

        data = self._check_recv(loads(m.data))

        if isinstance(data.get('data'), bool):
            return data['data']

        try:
            data['data'] = decompress(data['data'])
        except (TypeError, UncompressError):
            pass

        return data.get('data')

    def _send(self, mtype, data='[]', nowait=False, decode=True):

        if not self.is_connected:
            self.socket.connect(self.remote)

        self.is_connected = True

        if isinstance(data, str):
            data = data.encode('utf-8')

        self.socket.send_msg(Msg(mtype=mtype, data=data))

        if self.nowait or nowait:
            if self.autoclose:
                self.socket.close()
            return

        return self._recv(decode=decode, close=self.autoclose)
