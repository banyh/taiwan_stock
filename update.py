# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from datetime import timedelta, datetime, date

from crawler.exchange_FMTQIK import FMTQIK
from crawler.exchange_MI_INDEX import MI_INDEX
from crawler.exchange_MI_MARGN import MI_MARGN
from crawler.exchange_STOCK_DAY import STOCK_DAY
from crawler.fund_BFI82U import BFI82U

crawlers = [FMTQIK(), MI_INDEX(), MI_MARGN(), STOCK_DAY(), BFI82U()]
for c in crawlers:
    c.download(date.today() - timedelta(days=10))
