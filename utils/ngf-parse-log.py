#!/usr/bin/env python3
"""Parse timestamps from log file to convert it to ISO.

Usage:
  ngf-parse-log.py [--tz=TIMEZONE] [--prefix=PREFIX] [--config=CONFIG]
                   [--time-format=TIME_FORMAT]...
                   [<logfile>]...
  ngf-parse-log.py (-h | --help)
  ngf-parse-log.py --version

Argiments:
  <logfile>                     Log file to read [default: stdin].

Options:
  --config=CONFIG               Configuration file for ipinfo.io
                                [default: config.yaml]
  --prefix=PREFIX               Search prefix in logs [default: geo-filter].
  --tz=TIMEZONE                 Timezone of the timestamps in the log file
                                [default: America/Toronto].
  --time-format=TIME_FORMAT     Time format of the timestamps in the log file
                                [default: YYYY-MMM-DDTHH:mm:ss].
                                It can be specified multiple times.
  -h --help                     Show this screen.
  --version                     Show version.
"""
import os
import sys
import errno
import arrow
import dateutil
import configparser
from docopt import docopt

import ipinfo


def filter_line(line, prefix):
    if prefix:
        if prefix in line:
            return line
    else:
        return line


def read_input(logfiles, prefix=None):
    if not logfiles:
        lines = sys.stdin.readlines()
        for line in lines:
            res = filter_line(line, prefix)
            if res:
                yield res
    else:
        for infile in logfiles:
            infp = open(infile, 'r')
            for line in infp:
                res = filter_line(line, prefix)
                if res:
                    yield res


def find_src_ip(line):
    res = None
    for sub in line:
        if 'SRC' in sub:
            res = sub.split('=')[-1]

    return res


if __name__ == '__main__':
    arguments = docopt(__doc__, version='ngf-parse-log 0.2')
    logfiles = arguments['<logfile>']
    prefix = arguments['--prefix']
    tz = arguments['--tz']
    time_formats = arguments['--time-format']

    config_file = arguments['--config']
    config = configparser.ConfigParser()

    if not os.path.exists(config_file):
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), config_file)
    config.read(config_file)
    ipinfo_token = config['ipinfo']['token']
    ipinfo_handler = ipinfo.getHandler(ipinfo_token)

    ip_cache = {}
    for line in read_input(logfiles, prefix):
        line = line.split()

        year = arrow.now().year
        month = line[0]
        day = line[1]
        time = line[2]
        ip_address = find_src_ip(line)

        timestamp_str = ('{year}-{month}-{day}T{time}'
                         .format(year=year, month=month, day=day, time=time))
        timestamp = arrow.get(timestamp_str,
                              [tf for tf in time_formats]
                              ).replace(tzinfo=dateutil.tz.gettz(tz))

        if ip_address in ip_cache:
            country = ip_cache[ip_address]
        else:
            details = ipinfo_handler.getDetails(ip_address).all
            country = details['country']
            ip_cache[ip_address] = country

        print(timestamp, ip_address, country, flush=True)
