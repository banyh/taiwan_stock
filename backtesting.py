# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, timedelta
from dataset import dailydata

one_day = timedelta(days=1)


def backtest(broker, start_day, end_day, start_money):
    money = float(start_money)
    portfolio = defaultdict(int)
    today = start_day
    while today <= end_day:
        data = dailydata[today]
        actions = broker.append(data)
        for act, stock_id, price, num_shares in actions:
            if act == 'buy':
                money -= price * num_shares
                portfolio[stock_id] += num_shares
                assert money >= 0
                print('{!s}，以{}的價格買進{}股{}，餘額{}'.format(today, price, num_shares, stock_id, money))
            elif act == 'sell':
                portfolio[stock_id] -= num_shares
                money += price * num_shares
                assert portfolio[stock_id] >= 0
                print('{!s}，以{}的價格賣出{}股{}，餘額{}'.format(today, price, num_shares, stock_id, money))
        today += one_day

    # 結束時，賣出所有股票
    for stock_id in portfolio:
        if portfolio[stock_id] > 0:
            price = data[stock_id + '_收盤價']
            num_shares = portfolio[stock_id]
            money += price * num_shares
            print('{!s}，以{}的價格賣出{}股{}，餘額{}'.format(end_day, price, num_shares, stock_id, money))

    print('啟始資金={}，投資報酬率={:.2f}%'.format(start_money, money / start_money * 100))