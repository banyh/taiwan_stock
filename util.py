# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import requests
from requests import Timeout
import re
from subprocess import check_output, call
import attr
import time


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
                text = requests.get(url, headers=self.headers).text
            except Timeout:
                time.sleep(60 * 15)
            else:
                break
        self.increase_get_count()
        return text

    def increase_get_count(self):
        self.get_count += 1
        if self.get_count > 24:
            self.get_count = 0
            self.increase_loc_index()

    def increase_loc_index(self):
        self.locindex = (self.locindex + 1) % len(self.locations)
        call(['windscribe', 'connect', self.locations[self.locindex]])
        print('proxy connect to', self.locations[self.locindex])


def str_to_int(string):
    return int(string.replace(',', ''))


proxy = Proxy()