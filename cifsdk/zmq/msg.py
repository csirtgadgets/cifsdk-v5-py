import json
import logging
import os
from msgpack import packb, unpackb
from msgpack.exceptions import ExtraData
from cifsdk.zmq.utils import pack, unpack, mtype_to_int, MAP, DecimalDecoder

try:
    import zmq

except ImportError:
    print("Requires pyzmq")
    raise SystemExit

TRACE = os.getenv('CIFSDK_MSG_TRACE', False)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

if TRACE == '1':
    logger.setLevel(logging.DEBUG)


class Msg(object):

    INDICATORS_CREATE = 1
    INDICATORS_SEARCH = 2
    INDICATORS_DELETE = 3

    def __init__(self, **kwargs):
        for e in ['id', 'client_id', 'mtype', 'data']:
            if isinstance(kwargs.get(e), bytes):
                try:
                    kwargs[e] = kwargs[e].decode('utf-8')
                except:
                    pass
            setattr(self, e, kwargs.get(e))

        if isinstance(self.data, bytes):
            self.data = unpack(self.data)

    def __repr__(self):
        return json.dumps(self.__dict__(), cls=DecimalDecoder)

    def __dict__(self):
        return {
            'id': self.id,
            'mtype': self.mtype,
            'data': self.data,
        }

    def to_frame(self):
        m = []

        # check to see if we have a frame / client id
        for e in ['id', 'client_id']:
            if getattr(self, e):
                m.append(getattr(self, e))

        # insert a null
        if len(m) > 0:
            m.append(''.encode('utf-8'))

        # msg type
        if isinstance(self.mtype, bytes):
            self.mtype = mtype_to_int(self.mtype.decode('utf-8'))

        elif isinstance(self.mtype, str):
            self.mtype = mtype_to_int(self.mtype)

        m.append(packb(self.mtype))

        # pack it up
        if isinstance(self.data, dict):
            self.data = [self.data]

        m.append(pack(self.data))

        # encode all the strings
        for idx, v in enumerate(m):
            if isinstance(v, str):
                m[idx] = v.encode('utf-8')

        return m

    @staticmethod
    def from_frame(m):
        # zmq has diff frame types depending on
        if len(m) == 5:
            id, client_id, _, mtype, data = m
            return Msg(id=id, client_id=client_id, mtype=MAP[unpackb(mtype)],
                       data=unpack(data))

        if len(m) == 4:
            id, _, mtype, data = m
            return Msg(id=id, mtype=MAP[unpackb(mtype)], data=unpack(data))

        if len(m) == 3:
            id, mtype, data = m

            try:
                mtype = unpackb(mtype)

            except ExtraData:
                pass

            if len(id) > 10:
                return Msg(mtype=MAP[mtype], data=unpack(data))

            return Msg(id=id, mtype=MAP[mtype], data=unpack(data))

        mtype, data = m
        return Msg(mtype=mtype, data=unpack(data))
