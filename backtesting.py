# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from collections import defaultdict
from datetime import datetime, timedelta, date
from dataset import dailydata
from util import slack_log

one_day = timedelta(days=1)


def buy_fee(amount):
    """假設買進時的手續費是0.1425%"""
    return amount * 0.001425


def sell_fee(amount):
    """假設賣出時的手續費是0.1425%，交易稅是0.3%"""
    return amount * (0.001425 + 0.003)


def buy(broker, stock_id, price, num_shares):
    if num_shares == 'auto':
        num_shares = int(broker.money / (price * 1001.425)) * 1000

    broker.money -= price * num_shares + buy_fee(price * num_shares)
    # broker.portfolio_cost[stock_id] = (broker.portfolio_cost[stock_id] * broker.portfolio[stock_id] +
    #                                    price * num_shares) / (broker.portfolio[stock_id] + num_shares)
    broker.portfolio_cost[stock_id] = price
    broker.portfolio[stock_id] += num_shares
    if broker.portfolio[stock_id] == 0:
        del broker.portfolio[stock_id]
        del broker.portfolio_cost[stock_id]
    print('{}: 以{:8.3f}的價格買進{:8d}股"{}"，餘額{:.0f}'.format(broker.today, price, num_shares, stock_id, broker.money))


def sell(broker, stock_id, price, num_shares):
    if num_shares == 'auto':
        num_shares = broker.portfolio[stock_id]

    broker.portfolio[stock_id] -= num_shares
    broker.money += price * num_shares - sell_fee(price * num_shares)
    if broker.portfolio[stock_id] == 0:
        del broker.portfolio[stock_id]
        del broker.portfolio_cost[stock_id]
    print('{}: 以{:8.3f}的價格賣出{:8d}股"{}"，餘額{:.0f}'.format(broker.today, price, num_shares, stock_id, broker.money))


def backtest(broker, start_money, start_day=date(2017, 1, 1), end_day=date(2017, 12, 31)):
    broker.reset(start_money)
    today = start_day
    while today <= end_day:
        data = dailydata[today]
        if data['TradingDay']:
            last_trading_data = data
        else:
            today += timedelta(days=1)
            continue

        broker.predict()  # 所有要執行的動作，都放在 buy_at_open, buy_at_close...等6個list裡面
        broker.today = today

        while broker.buy_at_open:
            sid, n_shares = broker.buy_at_open.pop(0)
            buy(broker, sid, data[sid + '_開盤價'], n_shares)

        while broker.sell_at_open:
            sid, n_shares = broker.sell_at_open.pop(0)
            sell(broker, sid, data[sid + '_開盤價'], n_shares)

        while broker.buy_at_target:
            sid, n_shares, price = broker.buy_at_target.pop(0)
            if price > data[sid + '_最低價'] and price < data[sid + '_最高價']:
                buy(broker, sid, price, n_shares)
            else:
                broker.buy_at_close.append((sid, 'auto'))

        while broker.sell_at_target:
            sid, n_shares, price = broker.sell_at_target.pop(0)
            if price > data[sid + '_最低價'] and price < data[sid + '_最高價']:
                sell(broker, sid, price, n_shares)
            else:
                broker.sell_at_close.append((sid, 'auto'))

        for sid in broker.stop_loss_value:
            if broker.stop_loss_value[sid] == 0 or broker.portfolio[sid] == 0:
                continue
            low_cost = broker.portfolio_cost[sid] * (1 - broker.stop_loss_value[sid])
            high_cost = broker.portfolio_cost[sid] * (1 + broker.stop_loss_value[sid])
            if broker.portfolio[sid] > 0 and data[sid + '_最低價'] < low_cost:
                sell(broker, sid, low_cost, 'auto')
            if broker.portfolio[sid] < 0 and data[sid + '_最高價'] > high_cost:
                buy(broker, sid, low_cost, -broker.portfolio[sid])

        for sid in broker.take_profit_value:
            if broker.take_profit_value[sid] == 0 or broker.portfolio[sid] == 0:
                continue
            low_cost = broker.portfolio_cost[sid] * (1 - broker.take_profit_value[sid])
            high_cost = broker.portfolio_cost[sid] * (1 + broker.take_profit_value[sid])
            if broker.portfolio[sid] > 0 and data[sid + '_最高價'] > high_cost:
                sell(broker, sid, low_cost, 'auto')
            if broker.portfolio[sid] < 0 and data[sid + '_最低價'] < low_cost:
                buy(broker, sid, low_cost, -broker.portfolio[sid])

        while broker.buy_at_close:
            sid, n_shares = broker.buy_at_close.pop(0)
            buy(broker, sid, data[sid + '_收盤價'], n_shares)

        while broker.sell_at_close:
            sid, n_shares = broker.sell_at_close.pop(0)
            sell(broker, sid, data[sid + '_收盤價'], n_shares)

        broker.append(data)  # 補充今天的成交資料
        today += one_day

    # 測試期間結束時，以最後一個交易日的收盤價，賣出所有股票
    for stock_id in list(broker.portfolio.keys()):
        if broker.portfolio[stock_id] > 0:
            sell(broker, stock_id, last_trading_data[stock_id + '_收盤價'], 'auto')

    roi = broker.money / start_money * 100 - 100
    print('啟始資金={}，投資報酬率={:.2f}%'.format(start_money, roi))
    return roi
