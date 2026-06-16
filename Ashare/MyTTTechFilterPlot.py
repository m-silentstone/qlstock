import math

import matplotlib
import numpy as np
import pandas as pd

import MyUtils;import time
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import MyTT;
from Ashare import *

day_count = 1000
more_day_count = 60
stock_code = 'sh601728'
high_low_threshold = 0.05
high_low_day_threshold = 5
calc_date = '2025-05-30'
stock_code_index_start = 0
stock_code_index_end = 300

stock_list_file = 'all_stocks_hk.txt'

# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
# 负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
price_key = 'close'


def get_stock_data(stock_code, day_count, more_day_count, calc_date):
    """
    获取股票历史数据
    
    Args:
        stock_code: 股票代码
        day_count: 要获取的天数
        more_day_count: 额外获取的天数
    
    Returns:
        stock_map: 股票基本信息
        stock_price_df: 股票价格数据
    """
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        return None, None
    
    round_days = 300
    enddate_str = time.strftime('%Y-%m-%d', time.localtime())  # 结果包含end_date的价格
    if calc_date is not None:
        enddate_str = calc_date
    stock_price_df = MyUtils.get_price_tx(stock_code, end_date=enddate_str, frequency='1d',
                                          count=np.minimum(round_days, day_count + more_day_count))
    
    remain_days = day_count + more_day_count - len(stock_price_df)
    while remain_days > 0:
        element_end_date = (stock_price_df.index[0] + pd.Timedelta(days=-1)).strftime('%Y-%m-%d')
        element_stock_price_df = MyUtils.get_price_tx(stock_code, end_date=element_end_date, frequency='1d',
                                                      count=np.minimum(round_days, remain_days))
        if element_stock_price_df is None or len(element_stock_price_df) == 0:
            break
        remain_days = remain_days - len(element_stock_price_df)
        stock_price_df = pd.concat([element_stock_price_df, stock_price_df])
        time.sleep(0.2)
    
    return stock_map, stock_price_df



def filter_stock(stock_code, day_count):
    stock_map = MyUtils.get_from_gtime(stock_code)
    if 'pe' not in stock_map.keys() or 'total_market_value' not in stock_map.keys():
        return None
    if 0 < stock_map['pe'] <= 15 and stock_map['total_market_value'] >= 800:
        print(stock_code, stock_map['name'], stock_map['pe'],
              '--------------------------------------------------------')
        print(stock_map)
        return stock_map
    return None

def calc_stock_score(stock_map, day_count, stock_score_map):
    print('calc:', stock_map['code'])
    score = stock_map['pe']
    score_store(score, stock_map, stock_score_map)
    return

def score_store(score, stock_map, stock_score_map):
    stock_map_list = stock_score_map.get(score);
    if stock_map_list is None:
        stock_map_list = []
    stock_map_list.append(stock_map)
    stock_score_map[score] = stock_map_list

def plot_stocks(stock_score_map):
    for key in sorted(stock_score_map):
        print(key, stock_score_map[key])
    return

def stock_filter_calc_plot(day_count):
    if day_count < 2:
        print('计算历史时间太短！')
        return
    allstockcode_array = []
    stock_score_map = {}
    with open(stock_list_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[0:]:
            array = line.split()
            code_array = array[0].split('.')
            allstockcode_array.append(str(code_array[1] + code_array[0]).lower())
    stock_code_index = stock_code_index_start - 1
    while stock_code_index < len(allstockcode_array):
        if stock_code_index_end > 0 and stock_code_index >= stock_code_index_end:
            break
        stock_code_index = stock_code_index + 1
        print('stock_code_index:' + str(stock_code_index))
        stock_code = allstockcode_array[stock_code_index];
        stock_map = filter_stock(stock_code, day_count)
        if stock_map is None:
            continue
        calc_stock_score(stock_map, day_count, stock_score_map)
        time.sleep(0.1)
    plot_stocks(stock_score_map)

# 执行---------------------------------------------------------------------

stock_filter_calc_plot(day_count)



