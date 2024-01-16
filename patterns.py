import talib
import yfinance as yf
import pandas as pd
from pandas import Timestamp
import numpy as np

data_5m = yf.download('SOXL', start = '2023-12-01', end = '2024-01-01', interval = '5m')
data_15m = yf.download('SOXL', start = '2023-12-01', end = '2024-01-01', interval = '15m')
data_30m = yf.download('SOXL', start = '2023-12-01', end = '2024-01-01', interval = '30m')
data_60m = yf.download('SOXL', start = '2023-12-01', end = '2024-01-01', interval = '60m')
data_1d = yf.download('SOXL', start = '2023-10-23', end = '2024-01-01', interval = '1d')

rsis_5m = talib.RSI(data_5m['Close'], timeperiod=14)
rsis_15m = talib.RSI(data_15m['Close'], timeperiod=14)
rsis_30m = talib.RSI(data_30m['Close'], timeperiod=14)
rsis_60m = talib.RSI(data_60m['Close'], timeperiod=14)
rsis_1d = talib.RSI(data_1d['Close'], timeperiod=14)

rsismas_5m = talib.SMA(rsis_5m, timeperiod=14)
rsismas_15m = talib.SMA(rsis_15m, timeperiod=14)
rsismas_30m = talib.SMA(rsis_30m, timeperiod=14)
rsismas_60m = talib.SMA(rsis_60m, timeperiod=14)
rsismas_1d = talib.SMA(rsis_1d, timeperiod=14)

datetime_list = data_5m.index.tolist()

class Event:
    def __init__(self, date, close, rsi_5m, rsisma_5m, rsi_15m, rsisma_15m, 
                 rsi_30m, rsisma_30m, rsi_60m, rsisma_60m, rsi_1d, rsisma_1d):
        self.date = date
        self.close = close
        self.rsi_5m = rsi_5m
        self.rsisma_5m = rsisma_5m
        self.ratio_5m = rsi_5m / rsisma_5m
        self.rsi_15m = rsi_15m
        self.rsisma_15m = rsisma_15m
        self.ratio_15m = rsi_15m / rsisma_15m
        self.rsi_30m = rsi_30m
        self.rsisma_30m = rsisma_30m
        self.ratio_30m = rsi_30m / rsisma_30m
        self.rsi_60m = rsi_60m
        self.rsisma_60m = rsisma_60m
        self.ratio_60m = rsi_60m / rsisma_60m
        self.rsi_1d = rsi_1d
        self.rsisma_1d = rsisma_1d
        self.ratio_1d = rsi_1d / rsisma_1d

events = [Event(datetime_list[0], data_5m['Close'].get(0), rsis_5m.iloc[0], rsismas_5m.iloc[0], rsis_15m.iloc[0], 
                rsismas_15m.iloc[0], rsis_30m.iloc[0], rsismas_30m.iloc[0], rsis_60m.iloc[0], rsismas_60m.iloc[0],
               rsis_1d.iloc[27], rsismas_1d.iloc[27])]

#rsis_5m: rsi at 15:45 means rsi value at 15:50
#rsis_15m: rsi at 14:45 means rsi value at 15:00
#rsis_30m: rsi at 14:30 means rsi value at 15:00
#rsis_60m: rsi at 14:30 means rsi value at 15:30

rsi_15_counter = -2
rsi_30_counter = -5
rsi_1h_counter = -11
rsi_1d_counter = 1;

for num in range(1, data_5m.shape[0]):
    current_rsi_15m = rsis_15m[int((rsi_15_counter / 3))]
    current_rsisma_15m = rsismas_15m[int((rsi_15_counter / 3))]
    current_rsi_30m = rsis_30m[int((rsi_30_counter / 6))]
    current_rsisma_30m = rsismas_30m[int((rsi_30_counter / 6))]
    current_rsi_60m = rsis_60m[int((rsi_1h_counter / 12)) + 1]
    current_rsisma_60m = rsismas_60m[int((rsi_1h_counter / 12)) + 2]
    current_rsi_1d = rsis_1d[int((rsi_1d_counter / 78)) + 28]
    current_rsisma_1d = rsismas_1d[int((rsi_1d_counter / 78)) + 28]
    
    currentEvent = Event(datetime_list[num], data_5m['Close'].get(num), rsis_5m.iloc[num - 1], 
                         rsismas_5m.iloc[num - 1], current_rsi_15m, current_rsisma_15m, current_rsi_30m,
                        current_rsisma_30m, current_rsi_60m, current_rsisma_60m, current_rsi_1d,
                        current_rsisma_1d)
    
    rsi_15_counter += 1
    rsi_30_counter += 1
    rsi_1h_counter += 1
    rsi_1d_counter += 1
    events.append(currentEvent)

#note to self: rsisma_60m starts at index 312

def calculate_average(lst):
    if len(lst) == 0:
        return 0  # Handle the case where the list is empty to avoid division by zero error
    total = sum(lst)
    average = total / len(lst)
    return average

class ratio_profit:
    def __init__(self, entry_ratio, ratio, profit, num_trades, win_rate, average_profit, average_loss,
                greatest_profit, greatest_loss):
        self.entry_ratio = entry_ratio
        self.ratio = ratio
        self.profit = profit
        self.num_trades = num_trades
        self.win_rate = win_rate
        self.average_profit = average_profit
        self.average_loss = average_loss
        self.greatest_profit = greatest_profit
        self.greatest_loss = greatest_loss

ratio_profits = []

entry_ratio_values = np.arange(0.900, 1.100, 0.001)
ratio_values = np.arange(1.000, 1.200, 0.001)

for entry_ratio in entry_ratio_values:
    for ratio in ratio_values:
        entryIndices = []
        exitIndices = []
        trade_counter = 0
        holding_position = False
        all_profits = []
        all_losses = []
        
        for i in range(313, data_5m.shape[0]):
            min_ratio_prev = min([events[i-1].ratio_5m, events[i-1].ratio_15m, 
                                         events[i-1].ratio_30m, events[i-1].ratio_60m, events[i-1].ratio_1d])
            if holding_position == False:
                if '''hidden for IP reasons''':
                    entryIndices.append(i)
                    holding_position = True
            elif holding_position == True:
                if '''hidden for IP reasons''' events[i - 1].ratio_60m < events[i - 2].ratio_60m:
                    exitIndices.append(i)
                    trade_counter += 1
                    holding_position = False
        
        profit_multiplier = 1.00
        wins = 0
        win_rate = 0
        
        for date in range(0, len(exitIndices)):
            profit = events[exitIndices[date]].close / events[entryIndices[date]].close
            profit_multiplier *= profit
            if profit > 1.00:
                wins += 1
                all_profits.append(profit)
            else:
                all_losses.append(profit)
        if trade_counter != 0:
            win_rate = wins / trade_counter
        elif trade_counter == 0:
            win_rate = 0
        
        average_profit = 0
        average_loss = 0
        greatest_profit = 0
        greatest_loss = 0
        
        if len(all_profits) == 0:
            average_profit = 0
            greatest_profit = 0
        else:
            average_profit = calculate_average(all_profits)
            greatest_profit = max(all_profits)
        
        if len(all_losses) == 0:
            average_loss = 0
            greatest_loss = 0
        else:
            average_loss = calculate_average(all_losses)
            greatest_loss = min(all_losses)
        
        rp = ratio_profit(entry_ratio, ratio, profit_multiplier, trade_counter, win_rate,
                         average_profit, average_loss, greatest_profit, greatest_loss)
        
        if (trade_counter < 25):
            ratio_profits.append(rp)

max_profit_index = 0
for i in range(1, len(ratio_profits)):
    if ratio_profits[i].profit > ratio_profits[max_profit_index].profit:
        max_profit_index = i

print("entry ratio: ", ratio_profits[max_profit_index].entry_ratio)
print("ratio: ", ratio_profits[max_profit_index].ratio)
print("profit: ", ratio_profits[max_profit_index].profit)
print("num_trades: ", ratio_profits[max_profit_index].num_trades)
print("win_rate: ", ratio_profits[max_profit_index].win_rate)
print("average_profit: ", ratio_profits[max_profit_index].average_profit)
print("average_loss: ", ratio_profits[max_profit_index].average_loss)
print("greatest_profit: ", ratio_profits[max_profit_index].greatest_profit)
print("greatest_loss: ", ratio_profits[max_profit_index].greatest_loss)