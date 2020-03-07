
import os.path
import tempfile
from csirtg_indicator.constants import COLUMNS

from ._version import get_versions
VERSION = get_versions()['version']
del get_versions

TEMP_DIR = os.path.join(tempfile.gettempdir())
RUNTIME_PATH = os.getenv('CIF_RUNTIME_PATH', TEMP_DIR)
DATA_PATH = os.getenv('CIF_DATA_PATH', TEMP_DIR)

# Logging stuff
LOG_FORMAT = '%(asctime)s - %(levelname)s - ' \
             '%(name)s[%(lineno)s][%(threadName)s] - %(message)s'

LOGLEVEL = 'ERROR'
LOGLEVEL = os.getenv('CIF_LOGLEVEL', LOGLEVEL).upper()

# address stuff

REMOTE = 'http://localhost:5000'
REMOTE = os.getenv('CIF_REMOTE', REMOTE)

ROUTER_ADDR = "ipc://{}".format(os.path.join(RUNTIME_PATH, 'router.ipc'))
ROUTER_ADDR = os.getenv('CIF_ROUTER_ADDR', ROUTER_ADDR)

SEARCH_LIMIT = os.getenv('CIF_SEARCH_LIMIT', 500)

FORMAT = os.getenv('CIFSDK_FORMAT', 'table')

EXPERT = False
if os.getenv('CIF_EXPERT', '0') == '1':
    EXPERT = True

COLUMNS = os.getenv('CIFSDK_COLUMNS', COLUMNS)
if not isinstance(COLUMNS, list):
    COLUMNS = COLUMNS.split(',')


MAX_FIELD_SIZE = 30

VALID_FILTERS = ['indicator', 'itype', 'confidence', 'provider', 'limit',
                 'nolog', 'tags', 'days', 'hours', 'groups', 'reported_at',
                 'cc', 'asn', 'asn_desc', 'rdata', 'first_at', 'last_at',
                 'region', 'no_feed', 'days', 'hours', 'today',  'latitude',
                 'longitude', 'risk']

PROFILES = {
    'bind': {
        'format': 'bind',
        'confidence': 4,
        'itype': 'fqdn',
        'days': 45,
        'tags': 'phishing,malware,botnet',
        'limit': 250000,
    },
    'zeek': {
        'confidence': 3,
        'format': 'bro',
        'itype': 'ipv4',
        'days': 21,
        'limit': 250000,
    },
    'snort': {
        'confidence': 3,
        'itype': 'ipv4',
        'format': 'snort',
        'days': 21,
        'limit': 250000,
    },
    'firewall': {
        'format': 'csv',
        'itype': 'ipv4',
        'confidence': 4,
        'days': 21,
        'tags': 'scanner,bruteforce,botnet',
        'limit': 25000
    },
    'sem': {
        'format': 'csv',
        'confidence': 3,
        'hours': 1,
        'limit': 25000,
        'itype': 'ipv4',
    },
}

PROFILES['splunk'] = PROFILES['sem']
