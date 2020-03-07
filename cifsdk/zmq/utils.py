from msgpack import unpackb, packb
import json
try:
    from snappy import compress, decompress

except ImportError:
    print("Requires google snappy compression lib to be installed..")
    raise

MAP = {
    1: 'indicators_create',
    2: 'indicators_search',
    3: 'indicators_delete'
}


def pack(data):
    if type(data) not in [str, bytes, dict, list]:
        raise TypeError(f'data must be of stdlib type, not: {type(data)}')

    return compress(packb(data))


def unpack(data, raw=False):
    return unpackb(decompress(data), raw=raw)


def mtype_to_int(mtype):
    for m in MAP:
        if MAP[m] == mtype:
            return m


class DecimalDecoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, float):
            return str(o)

        return super(DecimalDecoder, self).default(o)
