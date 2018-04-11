# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from broker.base import BaseBroker
import numpy as np
from collections import defaultdict


class MAOnlyBroker(BaseBroker):
    """用MA5,MA10作判斷的交易員。
    """
    name = 'MAOnlyBroker'

    def __init__(self, stock_id):
        super(MAOnlyBroker, self).__init__()
        self.cache = []
        self.stock_id = stock_id
        self.OP = stock_id + '_開盤價'
        self.ED = stock_id + '_收盤價'
        self.HI = stock_id + '_最高價'
        self.LO = stock_id + '_最低價'

    def predict(self):
        if len(self.cache) < 10:  # 要累積10日的資料，才能計算MA10
            return []

        prices = np.array(self.cache)
        w5 = np.arange(5, 0, -1)
        w10 = np.arange(10, 0, -1)
        ma5 = (prices[-5:] * w5).sum() / w5.sum()
        ma10 = (prices[-10:] * w10).sum() / w10.sum()
        if ma5 > ma10:
            if self.money > self.cache[-1] * 1000:  # 如果至少能買一張
                self.buy_at_open.append((self.stock_id, 'auto'))  # 策略: 開盤時以市價買進
                self.stop_loss_value[self.stock_id] = 0.005  # 損失0.5%時停慣
        elif ma10 < ma5:
            if self.portfolio[self.stock_id] > 0:  # 如果持有任何股票
                self.sell_at_open.append((self.stock_id, 'auto'))  # 策略: 開盤時以市價賣出
                del self.stop_loss_value[self.stock_id]

    def append(self, one_day_data):
        if one_day_data['TradingDay']:
            self.cache.append(one_day_data[self.ED])
