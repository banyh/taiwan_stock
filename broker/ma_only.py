# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from broker.base import BaseBroker
import numpy as np


class MAOnlyBroker(BaseBroker):
    """用MA5,MA10作判斷的交易員。
    """
    def __init__(self, stock_id):
        self.cache = []
        self.stock_id = stock_id
        self.OP = stock_id + '_開盤價'
        self.ED = stock_id + '_收盤價'
        self.HI = stock_id + '_最高價'
        self.LO = stock_id + '_最低價'

    def append(self, one_day_data):
        if not one_day_data['TradingDay']:
            return []
        if len(self.cache) < 10:
            self.cache.append(one_day_data[self.ED])
            return []

        prices = np.array(self.cache)
        w5 = np.arange(5, 0, -1)
        w10 = np.arange(10, 0, -1)
        ma5 = (prices[-5:] * w5).sum() / w5.sum()
        ma10 = (prices[-10:] * w10).sum() / w10.sum()
        transaction = []
        if ma5 > ma10:
            n = int(self.money / (self.cache[-1] * 1000)) * 1000  # 要買進的張數
            if n > 0:
                transaction.append(('buy', self.stock_id, one_day_data[self.OP], n))
                # 停損點設為 -0.5%
                stop_loss_point = one_day_data[self.OP] * 0.995
                if one_day_data[self.ED] < stop_loss_point:
                    transaction.append(('sell', self.stock_id, stop_loss_point, n))
        elif ma10 <= ma5:
            n = self.portfolio[self.stock_id]  # 全部賣出
            if n > 0:
                transaction.append(('sell', self.stock_id, one_day_data[self.OP], n))
        self.cache.append(one_day_data[self.ED])
        return transaction
