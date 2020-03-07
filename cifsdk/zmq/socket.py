
from cifsdk.zmq.msg import Msg

import zmq


class Socket(zmq.Socket):

    def __init__(self, *args, **kwargs):
        zmq.Socket.__init__(self, *args, **kwargs)

        self.LINGER = 3000
        self.SNDTIMEO = 5000
        self.RCVTIMEO = 5000
        self.set_hwm(250)

    def send_msg(self, m, flags=0):
        if isinstance(m, Msg):
            m = m.to_frame()

        return self.send_multipart(m)

    def recv_msg(self, relay=False):
        m = self.recv_multipart()

        if relay:
            assert isinstance(relay, zmq.Socket) or isinstance(relay, Socket)
            return relay.send_msg(m)

        return Msg().from_frame(m)

    def reply(self, m, data=None):
        if data:
            m.data = data

        return self.send_msg(m)


class Context(zmq.Context):
    _socket_class = Socket


def main():
    ctx = Context()
    req = ctx.socket(zmq.REQ)
    rep = ctx.socket(zmq.REP)

    rep.bind('inproc://a')
    req.connect('inproc://a')
    A = [1, 2, 3, 4, 5, 6]

    # send/recv with pickle+zip
    req.send_compressed(A)
    B = rep.recv_compressed()

    print("Checking zipped pickle...")
    print(A == B)

    from pprint import pprint
    pprint(A)


if __name__ == '__main__':
    main()