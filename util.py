# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests
from requests import Timeout
import re
from subprocess import check_output, call
from datetime import date, timedelta
import attr
import time


class RetryException(Exception):
    pass


class HolidayException(Exception):
    pass


def get_windscribe_locations():
    loc = check_output(['windscribe', 'locations']).decode('utf8')
    return [re.split('  +', l)[1] for l in loc.split('\n')[1:] if l]


@attr.s
class Proxy(object):
    locindex = attr.ib(init=False, default=0)
    get_count = attr.ib(init=False, default=0)
    headers = attr.ib(init=False, default={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
    locations = attr.ib(init=False, default=attr.Factory(get_windscribe_locations))

    def __attrs_post_init__(self):
        requests.session().keep_alive = False
        loc = check_output(['windscribe', 'locations']).decode('utf8')
        self.locations = [re.split('  +', l)[1] for l in loc.split('\n')[1:] if l]

    def get(self, url):
        while True:
            try:
                resp = requests.get(url, headers=self.headers)
            except Timeout:
                time.sleep(60 * 15)
            else:
                break
        self.increase_get_count()
        return resp

    def increase_get_count(self):
        self.get_count += 1
        if self.get_count > 24:
            self.increase_loc_index()

    def increase_loc_index(self):
        self.locindex = (self.locindex + 1) % len(self.locations)
        self.get_count = 0
        call(['windscribe', 'connect', self.locations[self.locindex]])
        print('proxy connect to', self.locations[self.locindex])


@attr.s
class NoProxy(object):
    headers = attr.ib(init=False, default={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})

    def __attrs_post_init__(self):
        requests.session().keep_alive = False

    def get(self, url):
        return requests.get(url, headers=self.headers)


def str_to_int(string):
    if isinstance(string, int):
        return string
    return int(float(string.replace(',', ''))) if string[:2] != '--' else 0


def str_to_float(string):
    if isinstance(string, float):
        return string
    return float(string.replace(',', '')) if string[:2] != '--' else 0.0


def daily_update(n_days_before=10):
    from crawler.exchange_FMTQIK import FMTQIK
    from crawler.exchange_MI_INDEX import MI_INDEX
    from crawler.exchange_MI_MARGN import MI_MARGN
    from crawler.exchange_STOCK_DAY import STOCK_DAY
    from crawler.fund_BFI82U import BFI82U

    crawlers = [FMTQIK(), MI_INDEX(), MI_MARGN(), STOCK_DAY(), BFI82U()]
    for c in crawlers:
        c.download(date.today() - timedelta(days=n_days_before))


proxy = Proxy()