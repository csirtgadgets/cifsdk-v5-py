from base64 import b64decode
import json

basestring = (str, bytes)


def _check_data(msgs):
    if isinstance(msgs, list):
        return msgs

    if msgs.get('status', False) not in ['success', 'failure']:
        raise RuntimeError(msgs)

    if msgs.get('status') == 'failure':
        raise TypeError(msgs['message'])

    if msgs['data'] == '{}':
        msgs['data'] = []

    # check to see if it's straight elasticsearch json
    if isinstance(msgs['data'], basestring) and msgs['data']\
            .startswith('{"hits":{"hits":[{"_source":'):
        msgs['data'] = json.loads(msgs['data'])
        msgs['data'] = [r['_source'] for r in msgs['data']['hits']['hits']]

    if not isinstance(msgs['data'], list):
        msgs['data'] = [msgs['data']]

    for m in msgs['data']:
        if not isinstance(m, dict):
            continue

        if not m.get('message'):
            continue

        try:
            m['message'] = b64decode(m['message'])
        except Exception as e:
            pass

    return msgs


def _check_status(resp, expect=200):
    if resp.status_code == expect:
        return

    if resp.status_code == 400:
        r = json.loads(resp.text)
        raise TypeError(r['message'])

    if resp.status_code == 401:
        raise PermissionError('unauthorized')

    if resp.status_code == 404:
        raise LookupError('not found')

    if resp.status_code == 408:
        raise TimeoutError('timeout')

    if resp.status_code == 422:
        msg = json.loads(resp.text)
        raise ValueError(msg['message'])

    if resp.status_code == 429:
        raise ConnectionRefusedError('RateLimit exceeded')

    if resp.status_code in [503, 504]:
        raise ConnectionAbortedError('system seems busy..')

    if resp.status_code == 500:
        raise ConnectionError('System Error, Try again later..')

    if resp.status_code != expect:
        msg = 'unknown: %s' % resp.content
        raise RuntimeError(msg)
