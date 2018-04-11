# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from broker.base import BaseBroker
import numpy as np
from collections import defaultdict


class MAOnlyBroker(BaseBroker):
    """用MA5,MA10作判斷的交易員。
    """
    def __init__(self, stock_id):
        self.cache = []
        self.stock_id = stock_id
        self.stop_loss = defaultdict(float)
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
            n = int(self.money / (self.cache[-1] * 1000)) * 1000  # 可以買進的股數
            if n > 0:
                transaction.append(self.buy_at_open(self.stock_id))  # 策略: 以開盤價買進
                self.stop_loss[self.stock_id] = one_day_data[self.OP] * 0.995
        elif ma10 < ma5:
            n = self.portfolio[self.stock_id]  # 全部賣出
            if n > 0:
                transaction.append(self.sell_at_open(self.stock_id))  # 策略: 以開盤價賣出
                self.stop_loss[self.stock_id] = 0

        # 如果最低價跌過停損點，表示我們會被洗出場
        if self.portfolio[self.stock_id] > 0 and self.stop_loss[self.stock_id] > 0:
            stop_loss = self.stop_loss[self.stock_id]
            if one_day_data[self.LO] <= stop_loss:
                n = self.portfolio[self.stock_id]
                transaction.append(self.stoploss_at_target(self.stock_id, stop_loss))

        self.cache.append(one_day_data[self.ED])
        return transaction
