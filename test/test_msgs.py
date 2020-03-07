from cifsdk.zmq.msg import Msg
import zmq
from cifsdk.zmq.socket import Context
from cifsdk.zmq.utils import unpack
import msgpack


def test_msgs():

    def _send_multipart(m):
        assert msgpack.unpackb(m[0]) == Msg.INDICATORS_SEARCH
        assert unpack(m[1]) == []

    m = Msg(mtype=Msg.INDICATORS_SEARCH, data=[])

    ctx = Context()
    s = ctx.socket(zmq.REQ)
    s.send_multipart = _send_multipart

    s.send_msg(m)


def test_msgs_recv():

    def _recv_multipart():
        return Msg(id=msgpack.packb(1234),
                   mtype=Msg.INDICATORS_SEARCH, data=[]).to_frame()

    ctx = Context()
    s = ctx.socket(zmq.REQ)
    s.recv_multipart = _recv_multipart

    m = s.recv_msg()

    assert msgpack.unpackb(m.id) == 1234
    assert m.mtype == 'indicators_search'
    assert m.data == []
