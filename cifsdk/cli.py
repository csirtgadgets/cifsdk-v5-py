#!/usr/bin/env python3

import logging
import sys
import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from csirtg_indicator.format import FORMATS
from cifsdk.utils import setup_logging, get_argument_parser
from csirtg_indicator import Indicator
from cifsdk.client.http import HTTP as Client

from cifsdk.constants import REMOTE, SEARCH_LIMIT, FORMAT, COLUMNS, EXPERT, \
    PROFILES, VALID_FILTERS

from pprint import pprint

logger = logging.getLogger(__name__)


def _check_filters(filters):
    if not isinstance(filters, dict):
        return

    if EXPERT is True:
        return

    if filters.get('indicator'):
        return

    if not filters.get('itype'):
        print('\nmissing --itype\n\n')
        raise SystemExit

    if not filters.get('indicator') and not filters.get('tags'):
        print('\nmissing --tags '
              '[phishing|malware|botnet|scanner|pdns|whitelist|...]\n\n')
        raise SystemExit


def _search(cli, args, options, filters):

    if not args.profile:
        _check_filters(filters)

    fmt = options.get('format')
    if args.profile:
        for k, v in PROFILES[args.profile].items():
            if k == 'format':
                fmt = v
            else:
                filters[k] = v

    try:
        rv = cli.search(filters)

    except PermissionError:
        logger.error('unauthorized')

    except ConnectionRefusedError:
        print("\ncif-router is either too busy or requires a restart...")
        print("if the problem continues, try increasing the amount of memory "
              "and cpus for the system")
        print("\nhttps://github.com/csirtgadgets/cif-v5/wiki/FAQ\n"
              "https://csirtg.io/support\n")

        raise SystemExit

    except KeyboardInterrupt:
        pass

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(e, exc_info=True)

    else:
        for l in FORMATS[fmt](data=rv):
            print(l.rstrip("\n"))

    raise SystemExit


def _create(cli, args, options):
    print("submitting {0}".format(options.get("submit")))
    i = Indicator(indicator=args.indicator, tags=args.tags,
                  confidence=args.confidence)

    rv = cli.indicators_create(i)

    print('success id: {}\n'.format(rv))


def _delete(cli, args, filters):
    if args.id:
        filters = {'id': args.id}

    filters = {f: filters[f] for f in filters if filters.get(f)}
    print("deleting {0}".format(filters))
    rv = cli.indicators_delete(filters)

    print('deleted: {}'.format(rv))


def main():  # pragma: no cover
    p = get_argument_parser()
    p = ArgumentParser(
        description=textwrap.dedent('''\
        example usage:
            $ cif -q example.org -d
            $ cif --search 1.2.3.0/24
            $ cif --profile zeek
        '''),
        formatter_class=RawDescriptionHelpFormatter,
        prog='cif',
        parents=[p]
    )
    p.add_argument('--remote', help='specify API remote [default %(default)s]',
                   default=REMOTE)
    p.add_argument('--no-verify-ssl', action='store_true')

    p.add_argument("--create", action="store_true", help="create an indicator")
    p.add_argument('--delete', action='store_true')
    p.add_argument('-q', '--search', help="search")

    p.add_argument('--itype', help='filter by indicator type')
    p.add_argument('--reported_at', help='specify reported_at filter')

    p.add_argument('-n', '--nolog', help='do not log search',
                   action='store_true')

    p.add_argument('-f', '--format',
                   help='specify output format [default: %(default)s]"',
                   default=FORMAT, choices=FORMATS.keys())

    p.add_argument('--indicator', help='indicator (ip, url, etc..) '
                                       'to search for')
    p.add_argument('--confidence', help="specify confidence level")
    p.add_argument('--tags', nargs='+', help='filter by tag(s)')
    p.add_argument('--provider', help='provider to filter by')
    p.add_argument('--asn', help='filter by asn')
    p.add_argument('--cc', help='filter by country code')
    p.add_argument('--asn-name', help='filter by asn name')
    p.add_argument('--rdata', help='filter by rdata')
    p.add_argument('--groups', help='filter by group(s)')

    p.add_argument('--days', help='filter results within last X days')
    p.add_argument('--today', action='store_true',
                   help='auto-sets reported_at to today, 00:00:00Z (UTC)')

    p.add_argument('--limit', help='limit results [default %(default)s]',
                   default=SEARCH_LIMIT)

    p.add_argument('--columns',  default=','.join(COLUMNS),
                   help='specify output columns [default %(default)s]')

    p.add_argument('--no-feed', action='store_true',
                   help='return a non-filtered dataset (no whitelist applied)')

    p.add_argument('--profile', help='specify feed profile',
                   choices=PROFILES.keys())

    args = p.parse_args()

    setup_logging(args)

    opts = vars(args)

    options = {}
    for k, v in opts.items():
        if v:
            options[k] = v

    if args.remote.startswith('http'):
        verify_ssl = True
        if args.no_verify_ssl:
            verify_ssl = False

        if args.remote == 'https://localhost':
            verify_ssl = False

        cli = Client(verify_ssl=verify_ssl)

    else:
        from cifsdk.client.zeromq import ZMQ
        cli = ZMQ()

    filters = {e: options.get(e) for e in VALID_FILTERS}

    if args.search:
        filters['indicator'] = args.search

    for k, v in filters.items():
        if v is True:
            filters[k] = 1

        if v is False:
            filters[k] = 0

    if options.get("create"):
        _create(cli, args, filters)
        raise SystemExit

    if options.get("delete"):
        _delete(cli, args, filters)
        raise SystemExit

    if not sys.stdin.isatty():
        buffer = sys.stdin.read().rstrip("\n").split("\n")

        filters = [{'indicator': i} for i in buffer]

    _search(cli, args, options, filters)


if __name__ == "__main__":
    main()
