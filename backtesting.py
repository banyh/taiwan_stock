# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import defaultdict
from datetime import datetime, timedelta, date
from dataset import dailydata

one_day = timedelta(days=1)


def backtest(broker, start_money, start_day=date(2017, 1, 1), end_day=date(2017, 12, 31)):
    broker.money = float(start_money)
    broker.portfolio = defaultdict(int)
    today = start_day
    while today <= end_day:
        data = dailydata[today]
        if data['TradingDay']:
            last_trading_data = data
        actions = broker.append(data)
        for act, stock_id, price, num_shares in actions:
            if act == 'buy':
                broker.money -= price * num_shares
                broker.portfolio[stock_id] += num_shares
                assert broker.money >= 0
                print('{!s}，以{}的價格買進{}股{}，餘額{}'.format(today, price, num_shares, stock_id, broker.money))
            elif act == 'sell':
                broker.portfolio[stock_id] -= num_shares
                broker.money += price * num_shares
                assert broker.portfolio[stock_id] >= 0
                print('{!s}，以{}的價格賣出{}股{}，餘額{}'.format(today, price, num_shares, stock_id, broker.money))
        today += one_day

    # 結束時，賣出所有股票
    for stock_id in broker.portfolio:
        if broker.portfolio[stock_id] > 0:
            price = last_trading_data[stock_id + '_收盤價']
            num_shares = broker.portfolio[stock_id]
            broker.money += price * num_shares
            print('以{}的價格賣出{}股{}，餘額{}'.format(price, num_shares, stock_id, broker.money))

    print('啟始資金={}，投資報酬率={:.2f}%'.format(start_money, broker.money / start_money * 100 - 100))