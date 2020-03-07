import logging
import requests
import json
from time import sleep
import random

from cifsdk.constants import VERSION, REMOTE

from cifsdk.client.http.utils import _check_data, _check_status
from pprint import pprint

from .constants import RETRIES_DELAY, TRACE, TIMEOUT, RETRIES

s, e = RETRIES_DELAY.split(',')
RETRIES_DELAY = random.uniform(int(s), int(e))

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger(__name__)

logger.setLevel(logging.WARNING)
logging.getLogger('requests.packages.urllib3.connectionpool')\
    .setLevel(logging.ERROR)

if TRACE:
    logger.setLevel(logging.DEBUG)
    logging.getLogger('requests.packages.urllib3.connectionpool')\
        .setLevel(logging.DEBUG)


class Base(object):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self

    def __init__(self, timeout=int(TIMEOUT), **kwargs):
        self.proxy = kwargs.get('proxy')
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.nowait = kwargs.get('nowait', False)
        self.timeout = timeout

        self.remote = kwargs.get('remote', REMOTE)

        self.session = requests.Session()
        self.session.headers["Accept"] = 'application/vnd.cif.v5+json'
        self.session.headers['User-Agent'] = 'cifsdk-py/{}'.format(VERSION)
        self.session.headers['Accept-Encoding'] = 'deflate'

    def __get(self, uri, params):
        resp = self.session.get(uri, params=params, verify=self.verify_ssl,
                                timeout=self.timeout)
        logger.debug(resp.text)
        n = RETRIES
        try:
            _check_status(resp, expect=200)
            n = 0
            return resp

        except Exception as e:
            if resp.status_code == 429 or resp.status_code in [503, 504]:
                logger.error(e)
            else:
                raise e

        for nn in (1, n):
            logger.warning('setting random retry interval..')
            logger.warning('retrying in %.00fs' % RETRIES_DELAY)
            sleep(RETRIES_DELAY)

            resp = self.session.get(uri, params=params, verify=self.verify_ssl,
                                    timeout=self.timeout)
            if resp.status_code == 200:
                break

            if nn == n:
                raise ConnectionAbortedError('system seems busy.. try again '
                                             'later')

        return resp

    def _get(self, uri, params={}, retry=True):
        if not uri.startswith('http'):
            uri = "%s/%s" % (self.remote, uri)

        resp = self.__get(uri, params)

        data = resp.content

        ss = (int(resp.headers['Content-Length']) / 1024 / 1024)
        logger.info('processing %.2f megs' % ss)

        return _check_data(json.loads(data.decode('utf-8')))

    def _post(self, uri, data, expect=201):
        if not uri.startswith('http'):
            uri = "%s/%s" % (self.remote, uri)

        data = json.dumps(data)

        if self.nowait:
            uri = '{}?nowait=1'.format(uri)

        if isinstance(data, str):
            data = data.encode('utf-8')

        headers = {'Content-Type': 'application/json'}
        logger.debug('submitting')
        resp = self.session.post(uri, data=data, verify=self.verify_ssl,
                                 headers=headers, timeout=self.timeout)
        logger.debug(resp.content)
        logger.debug(resp.status_code)
        n = RETRIES
        try:
            _check_status(resp, expect=expect)
            n = 0

        except Exception as e:
            if resp.status_code == 429 or resp.status_code in [503, 504]:
                logger.error(e)
            else:
                raise e

        while n != 0:
            logger.info('setting random retry interval to spread out the load')
            logger.info('retrying in %.00fs' % RETRIES_DELAY)
            sleep(RETRIES_DELAY)

            resp = self.session.post(uri, data=data, verify=self.verify_ssl,
                                     headers=headers, timeout=self.timeout)

            if resp.status_code in [200, 201]:
                break

            if n == 0:
                logger.warning('system seems busy.. try again later')
                raise ConnectionRefusedError

        return json.loads(resp.content.decode('utf-8'))

    def _delete(self, uri, params={}):
        if not uri.startswith('http'):
            uri = "%s/%s" % (self.remote, uri)

        params = {f: params[f] for f in params if params.get(f)}

        for f in ['nolog', 'limit']:
            if params.get(f):
                del params[f]

        resp = self.session.delete(uri, data=json.dumps(params),
                                   verify=self.verify_ssl,
                                   timeout=self.timeout)
        _check_status(resp)
        return json.loads(resp.content.decode('utf-8'))

    def _put(self, uri, data):
        if not uri.startswith('http'):
            uri = "%s/%s" % (self.remote, uri)

        resp = self.session.put(uri, data=json.dumps(data))
        _check_status(resp)
        return json.loads(resp.content)
