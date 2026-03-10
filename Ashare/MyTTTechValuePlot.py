import math

import matplotlib
import numpy as np
import pandas as pd

import MyUtils;import time
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import MyTT;
from Ashare import *

day_count = 3000
more_day_count = 30
stock_code = 'sh000905'
high_low_threshold = 0.1
# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
# 负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
price_key = 'close'


def get_stock_data(stock_code, day_count, more_day_count):
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


def calculate_indicators(stock_price_df):
    """
    计算各种技术指标
    
    Args:
        stock_price_df: 股票价格数据
    
    Returns:
        stock_price_df: 添加了技术指标的股票价格数据
    """
    # 提取基础数据到数组，减少重复访问DataFrame
    CLOSE = stock_price_df.close.values
    HIGH = stock_price_df.high.values
    LOW = stock_price_df.low.values
    VOLUME = stock_price_df.volume.values
    
    # 价格移动平均线
    stock_price_df['MA5'] = MyUtils.ma(CLOSE, 5)
    stock_price_df['MA10'] = MyUtils.ma(CLOSE, 10)
    stock_price_df['MA20'] = MyUtils.ma(CLOSE, 20)
    stock_price_df['MA30'] = MyUtils.ma(CLOSE, 30)
    
    # 成交量移动平均线
    stock_price_df['VMA5'] = MyUtils.ma(VOLUME, 5)
    stock_price_df['VMA10'] = MyUtils.ma(VOLUME, 10)
    stock_price_df['VMA20'] = MyUtils.ma(VOLUME, 20)
    stock_price_df['VMA30'] = MyUtils.ma(VOLUME, 30)
    
    # 乖离率
    stock_price_df['BIAS6'] = MyUtils.bias(CLOSE, 6)
    stock_price_df['BIAS12'] = MyUtils.bias(CLOSE, 12)
    stock_price_df['BIAS24'] = MyUtils.bias(CLOSE, 24)
    
    # RSI相对强弱指数
    stock_price_df['RSI24'] = MyUtils.rsi(CLOSE, 24)
    
    # CCI 商品通道指数
    stock_price_df['CCI14'] = MyUtils.cci(CLOSE, HIGH, LOW)
    
    # DMA 移动平均线差
    DMA_DIF, DMA_DIFMA = MyUtils.dma(CLOSE)
    stock_price_df['DMA_DIF'] = DMA_DIF
    stock_price_df['DMA_DIFMA'] = DMA_DIFMA
    
    # WR 威廉指数
    stock_price_df['WR10'] = MyUtils.wr(CLOSE, HIGH, LOW, 10)
    stock_price_df['WR6'] = MyUtils.wr(CLOSE, HIGH, LOW, 6)
    
    # ENE-S
    ENE_UPPER, ENE_MID, ENE_LOWER = MyUtils.ene(CLOSE)
    stock_price_df['ENE_UPPER'] = ENE_UPPER
    stock_price_df['ENE_MID'] = ENE_MID
    stock_price_df['ENE_LOWER'] = ENE_LOWER
    
    # 布林带
    BOLL_UPPER, BOLL_MID, BOLL_LOWER = MyUtils.boll(CLOSE)
    stock_price_df['BOLL_UPPER'] = BOLL_UPPER
    stock_price_df['BOLL_MID'] = BOLL_MID
    stock_price_df['BOLL_LOWER'] = BOLL_LOWER
    
    # MACD
    DIF, DEA, MACD = MyUtils.macd(CLOSE)
    stock_price_df['DIF'] = DIF
    stock_price_df['DEA'] = DEA
    stock_price_df['MACD'] = MACD
    
    # VMACD
    VDIF, VDEA, VMACD = MyUtils.vmacd(CLOSE, VOLUME)
    stock_price_df['VDIF'] = VDIF
    stock_price_df['VDEA'] = VDEA
    stock_price_df['VMACD'] = VMACD
    
    # KDJ
    KDJ_K, KDJ_D, KDJ_J = MyUtils.kdj(CLOSE, HIGH, LOW)
    stock_price_df['KDJ_K'] = KDJ_K
    stock_price_df['KDJ_D'] = KDJ_D
    stock_price_df['KDJ_J'] = KDJ_J
    
    # ATR
    stock_price_df['ATR14'] = MyUtils.atr(CLOSE, HIGH, LOW, 14)
    
    # MFI
    stock_price_df['MFI'] = MyUtils.mfi(CLOSE, HIGH, LOW, VOLUME, 14)
    
    return stock_price_df


def calculate_trend_points(stock_price_df, high_low_threshold, price_key):
    """
    计算趋势高低点
    
    Args:
        stock_price_df: 股票价格数据
        high_low_threshold: 高低点阈值
        price_key: 价格键名
    
    Returns:
        hlpoint_map: 趋势高低点数据
    """
    hlpoint_map = {
        'change_price': [],
        'change_ratio': [],
        'change_day_length': [],
        'change_date': []
    }

    current_price = stock_price_df.iloc[0][price_key]
    current_date = stock_price_df.index[0]
    end_date = stock_price_df.index[-1]
    print('起始：', current_date.strftime('%Y-%m-%d'), current_price, '结束日期', end_date.strftime('%Y-%m-%d'), stock_price_df.iloc[-1][price_key])
    
    # 初始化第一个点
    hlpoint_map['change_price'].append(stock_price_df.iloc[0][price_key])
    hlpoint_map['change_date'].append(stock_price_df.index[0])
    hlpoint_map['change_ratio'].append(0.0)
    hlpoint_map['change_day_length'].append(0)
    
    hlpoint_map_flag = None
    
    for index, row in stock_price_df.iterrows():
        # 趋势高低点
        change_ratio = (stock_price_df.loc[index, price_key] - current_price) * 1.0 / current_price
        
        if hlpoint_map_flag is None:
            if change_ratio > high_low_threshold:
                hlpoint_map_flag = 'up'
                current_price = stock_price_df.loc[index, price_key]
                current_date = index
            elif change_ratio * (-1.0) > high_low_threshold:
                hlpoint_map_flag = 'down'
                current_price = stock_price_df.loc[index, price_key]
                current_date = index
        else:
            if hlpoint_map_flag == 'up':
                if current_price < stock_price_df.loc[index, price_key]:
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                elif change_ratio * (-1.0) > high_low_threshold:
                    # 记录高点并转向
                    hlpoint_map['change_price'].append(current_price)
                    hlpoint_map['change_date'].append(current_date)
                    hlpoint_map['change_ratio'].append((hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
                    hlpoint_map['change_day_length'].append(int((hlpoint_map['change_date'][-1] - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'd')))
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                    hlpoint_map_flag = 'down'
            elif hlpoint_map_flag == 'down':
                if current_price > stock_price_df.loc[index, price_key]:
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                elif change_ratio > high_low_threshold:
                    # 记录低点并转向
                    hlpoint_map['change_price'].append(current_price)
                    hlpoint_map['change_date'].append(current_date)
                    hlpoint_map['change_ratio'].append((hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
                    hlpoint_map['change_day_length'].append(int((hlpoint_map['change_date'][-1] - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'd')))
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                    hlpoint_map_flag = 'up'
    
    # 添加最后一个点
    hlpoint_map['change_price'].append(stock_price_df.iloc[-1][price_key])
    hlpoint_map['change_date'].append(stock_price_df.index[-1])
    hlpoint_map['change_ratio'].append((hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
    hlpoint_map['change_day_length'].append(
        int((hlpoint_map['change_date'][-1] - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'd')))
    
    return hlpoint_map


def plot_trend(stock_price_df, hlpoint_map, stock_code, stock_name, price_key):
    """
    绘制趋势图
    
    Args:
        stock_price_df: 股票价格数据
        hlpoint_map: 趋势高低点数据
        stock_code: 股票代码
        stock_name: 股票名称
        price_key: 价格键名
    """
    plt.title("趋势点")
    plt.ylabel(f"{stock_code}  {stock_name}")
    
    # 绘制价格线
    plt.plot(stock_price_df.index, stock_price_df[price_key], marker=',')
    
    # 绘制布林带
    plt.plot(stock_price_df.index, stock_price_df['BOLL_UPPER'].values, 'k--')
    plt.plot(stock_price_df.index, stock_price_df['BOLL_MID'].values, 'k--')
    plt.plot(stock_price_df.index, stock_price_df['BOLL_LOWER'].values, 'k--')
    
    # 绘制趋势点
    plt.plot(hlpoint_map['change_date'], hlpoint_map['change_price'], 'r^')
    
    # 添加趋势点标注
    for date, price, ratio, daylength in zip(
        hlpoint_map['change_date'], 
        hlpoint_map['change_price'], 
        hlpoint_map['change_ratio'], 
        hlpoint_map['change_day_length']
    ):
        plt.text(
            date, 
            price + 3, 
            '({},{},{}%,{}days)'.format(date.strftime("%Y-%m-%d"), np.round(price, 3), round(ratio * 100, 2), daylength)
        )
    
    plt.tight_layout()
    plt.show()


def stock_plot(stock_code, high_low_threshold, day_count):
    """
    绘制股票趋势图
    
    Args:
        stock_code: 股票代码
        high_low_threshold: 高低点阈值
        day_count: 要分析的天数
    """
    if day_count < 2:
        print('计算历史时间太短！')
        return
    
    stock_map, stock_price_df = get_stock_data(stock_code, day_count, more_day_count)
    if stock_map is None or stock_price_df is None:
        return

    print(stock_code, stock_map['name'], '--------------------------------------------------------')
    
    # 计算技术指标
    stock_price_df = calculate_indicators(stock_price_df)

    # 计算趋势高低点
    stock_price_df = stock_price_df[more_day_count:]
    print('数据长度:', len(stock_price_df))
    hlpoint_map = calculate_trend_points(stock_price_df, high_low_threshold, price_key)
    
    # 绘制趋势图
    plot_trend(stock_price_df, hlpoint_map, stock_code, stock_map['name'], price_key)

# 执行---------------------------------------------------------------------
stock_plot(stock_code, high_low_threshold, day_count)



