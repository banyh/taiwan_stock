# -*- coding: utf-8 -*-
"""程式交易員的基本類別。
"""
from __future__ import unicode_literals, print_function
from collections import defaultdict


class BaseBroker(object):
    """這是交易員的 base class。
    當回測開始時，回測程式會設定 broker.money(持有的現金) 及 broker.portfolio(持有的投資組合)。
    每一天，回測程式會呼叫append，交易員應該根據過去的資料，決定這一天要進行的交易，並傳回給回測。
    """
    def reset(self, money=0.0):
        self.money = money
        self.portfolio = defaultdict(int)  # mapping "stock_id" --> num_shares
        self.portfolio_cost = defaultdict(float)  # mapping "stock_id" --> price_at_buying
        self.stop_loss_value = defaultdict(float)  # mapping "stock_id" --> stop loss value
        self.take_profit_value = defaultdict(float)  # mapping "stock_id" --> take profit value

        self.buy_at_open = list()  # list of (stock_id, num_shares) 開盤時以市價買入
        self.buy_at_close = list()  # list of (stock_id, num_shares) 收盤時以市價買入
        self.buy_at_target = list()  # list of (stock_id, num_shares, price) 設法以目標價買入，如果目標價超過當日的價格區間，則以收盤價買入。
        self.sell_at_open = list()  # list of (stock_id, num_shares) 開盤時以市價賣出
        self.sell_at_close = list()  # list of (stock_id, num_shares) 收盤時以市價賣出
        self.sell_at_target = list()  # list of (stock_id, num_shares, price) 設法以目標價賣出，如果目標價超過當日的價格區間，則以收盤價賣出。

    def __init__(self):
        self.reset()

    def predict(self):
        """根據目前cache中的歷史資料，預測明天要進行的交易。
        """
        raise NotImplementedError

    def append(self, one_day_data):
        """輸入「今天」的價格資料，傳回要進行的動作，並將今天的資料存入cache。
        動作的範例: [('buy', '0050', 53.20, 2000), ('sell', '2002', 21.80, 1000)]
        表示以53.2的價格買入2張0050，以21.8的價格賣出1張2002。
        注意：買入的花費不應超過 self.money，賣出的股票一定要存在於 self.portfolio。
        """
        raise NotImplementedError

    def message(self):
        msgs = []
        for sid, n in self.buy_at_open:
            msgs.append('[{}] 開盤時，掛市價單，買進{}股"{}"'.format(self.name, n, sid))
        for sid, n in self.sell_at_open:
            msgs.append('[{}] 開盤時，掛市價單，賣出{}股"{}"'.format(self.name, n, sid))
        for sid, n, price in self.buy_at_target:
            msgs.append('[{}] 盤中掛{}的買單，買進{}股"{}"'.format(self.name, price, n, sid))
        for sid, n, price in self.sell_at_target:
            msgs.append('[{}] 盤中掛{}的賣單，賣出{}股"{}"'.format(self.name, price, n, sid))
        for sid, n in self.buy_at_close:
            msgs.append('[{}] 收盤時，掛市價單，買進{}股"{}"'.format(self.name, n, sid))
        for sid, n in self.sell_at_close:
            msgs.append('[{}] 收盤時，掛市價單，賣出{}股"{}"'.format(self.name, n, sid))
        return msgs
