import math

import matplotlib
import numpy as np
from pandas.core.interchange.dataframe_protocol import DataFrame

import MyUtils;import time;
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import MyTT;
from Ashare import *

day_count=1000
stock_code='sh000905'
high_low_threshhold = 0.03
# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
more_day_count = 30


def stock_plot(stock_code, high_low_threshhold, day_count):
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count+more_day_count)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        return
    print(stock_code, stock_map['name'],'--------------------------------------------------------')
    #日线
    CLOSE=stock_price_df.close.values
    HIGH=stock_price_df.high.values
    LOW=stock_price_df.low.values

    VOLUME=stock_price_df.volume.values
    # 价格日线
    MA5 = MyUtils.ma(CLOSE, 5)
    MA10 = MyUtils.ma(CLOSE, 10)
    MA20 = MyUtils.ma(CLOSE, 20)
    MA30 = MyUtils.ma(CLOSE, 30)
    stock_price_df['MA5']=MA5
    stock_price_df['MA10']=MA10
    stock_price_df['MA20']=MA20
    stock_price_df['MA30']=MA30

    # 成交量日线
    VMA5 = MyUtils.ma(VOLUME, 5)
    VMA10 = MyUtils.ma(VOLUME, 10)
    VMA20 = MyUtils.ma(VOLUME, 20)
    VMA30 = MyUtils.ma(VOLUME, 30)
    stock_price_df['VMA5']=VMA5
    stock_price_df['VMA10']=VMA10
    stock_price_df['VMA20']=VMA20
    stock_price_df['VMA30']=VMA30

    # 乖离率
    BIAS6=MyUtils.bias(CLOSE, 6)
    BIAS12 = MyUtils.bias(CLOSE, 12)
    BIAS24 = MyUtils.bias(CLOSE, 24)
    stock_price_df['BIAS6']=BIAS6
    stock_price_df['BIAS12']=BIAS12
    stock_price_df['BIAS24']=BIAS24

    # RSI相对强弱指数
    RSI24 = MyUtils.rsi(CLOSE, 24)
    stock_price_df['RSI24']=RSI24

    # CCI 商品通道指数
    CCI14 = MyUtils.cci(CLOSE, HIGH, LOW)
    stock_price_df['CCI14']=CCI14

    # DMA 移动平均线差
    DMA_DIF, DMA_DIFMA = MyUtils.dma(CLOSE)
    stock_price_df['DMA_DIF'] = DMA_DIF
    stock_price_df['DMA_DIFMA'] = DMA_DIFMA

    # WR 威廉指数
    WR10 = MyUtils.wr(CLOSE, HIGH, LOW, 10)
    stock_price_df['WR10']=WR10
    WR6 = MyUtils.wr(CLOSE, HIGH, LOW, 6)
    stock_price_df['WR6']=WR6

    # ENE-S
    ENE_UPPER, ENE_MID, ENE_LOWER = MyUtils.ene(CLOSE)
    stock_price_df['ENE_UPPER']=ENE_UPPER
    stock_price_df['ENE_MID']=ENE_MID
    stock_price_df['ENE_LOWER']=ENE_LOWER

    # 布林带
    BOLL_UPPER,BOLL_MID,BOLL_LOWER = MyUtils.boll(CLOSE)
    stock_price_df['BOLL_UPPER']=BOLL_UPPER
    stock_price_df['BOLL_MID']=BOLL_MID
    stock_price_df['BOLL_LOWER']=BOLL_LOWER

    # MACD
    DIF, DEA, MACD= MyUtils.macd(CLOSE)
    stock_price_df['DIF']=DIF
    stock_price_df['DEA']=DEA
    stock_price_df['MACD']=MACD

    # VMACD
    VDIF, VDEA, VMACD= MyUtils.vmacd(CLOSE, VOLUME)
    stock_price_df['VDIF']=VDIF
    stock_price_df['VDEA']=VDEA
    stock_price_df['VMACD']=VMACD

    # KDJ
    KDJ_K,KDJ_D,KDJ_J=MyUtils.kdj(CLOSE,HIGH,LOW)
    stock_price_df['KDJ_K'] = KDJ_K
    stock_price_df['KDJ_D'] = KDJ_D
    stock_price_df['KDJ_J'] = KDJ_J

    # ATR
    ATR14 = MyUtils.atr(CLOSE, HIGH, LOW, 14)
    stock_price_df['ATR14'] = ATR14

    # MFI
    MFI = MyUtils.mfi(CLOSE,HIGH,LOW,VOLUME,14)
    stock_price_df['MFI'] = MFI

    stock_price_df = stock_price_df[more_day_count:]
    hlpoint_map = {}
    price_key = 'MA5'
    hlpoint_map['change_price'] = []
    hlpoint_map['change_ratio'] = []
    hlpoint_map['change_date'] = []

    current_price = stock_price_df.iloc[0][price_key]
    current_date = stock_price_df.index[0]
    hlpoint_map['change_price'].append(stock_price_df.iloc[0][price_key])
    hlpoint_map['change_date'].append(stock_price_df.index[0])
    hlpoint_map['change_ratio'].append(0.0)
    hlpoint_map_flag = None
    for index, row in stock_price_df.iterrows():
        '''
        # status列
        change=abs(float(row['close'])-float(row['open']))
        upline=float(row['high'])-max(float(row['close']),float(row['open']))
        downline = min(float(row['close']), float(row['open'])) - float(row['low'])
        stock_price_df.loc[index, 'status']=''
        isSkip=False
        for value in row.values:
            if math.isnan(value):
                isSkip=True
                break
        if isSkip:
            continue
        if row['MA5'] > row['MA20']:
            stock_price_df.loc[index, 'status'] += '价格金叉,' #上涨状态
        if row['MA5'] < row['MA20']:
            stock_price_df.loc[index, 'status'] += '价格死叉,' #下跌状态
        if upline > change * 2 and upline/float(row['close']) > 0.03:
            stock_price_df.loc[index, 'status'] += '上插针,' #上插针
        if downline > change * 2 and downline/float(row['close']) > 0.03:
            stock_price_df.loc[index, 'status'] += '下插针,' #下插针
        if row['close'] > row['BOLL_UPPER']:
            stock_price_df.loc[index, 'status'] += '布林带上超出,' #布林带上超出
        elif row['close'] > 0.75 * row['BOLL_UPPER'] + 0.25 * row['BOLL_MID']:
            stock_price_df.loc[index, 'status'] += '布林带上沿,' #布林带上沿
        elif row['close'] > row['BOLL_MID']:
            stock_price_df.loc[index, 'status'] += '布林带上半区,' #布林带上半区
        if row['close'] < row['BOLL_LOWER']:
            stock_price_df.loc[index, 'status'] += '布林带下超出,' #布林带下超出
        elif row['close'] < 0.75 * row['BOLL_LOWER'] + 0.25 * row['BOLL_MID']:
            stock_price_df.loc[index, 'status'] += '布林带下沿,' #布林带下沿
        elif row['close'] < row['BOLL_MID']:
            stock_price_df.loc[index, 'status'] += '布林带下半区,' #布林带下半区
        if row['RSI24'] > 65 or row['RSI24'] < 35:
            stock_price_df.loc[index, 'status'] += 'RSI='+str(row['RSI24'])+','
        '''
        # 趋势高低点
        change_ratio = round((stock_price_df.loc[index, price_key] - current_price) * 1.0 / current_price, 2)
        # print('高低点判断：', index, stock_price_df.loc[index, price_key], current_price, change_ratio)
        if hlpoint_map_flag is None:
            if change_ratio >= high_low_threshhold:
                hlpoint_map_flag = 'up'
                current_price = stock_price_df.loc[index, price_key]
                current_date = index
            elif change_ratio*(-1.0) >= high_low_threshhold:
                hlpoint_map_flag = 'down'
                current_price = stock_price_df.loc[index, price_key]
                current_date = index
        else:
            if hlpoint_map_flag == 'up':
                if current_price < stock_price_df.loc[index, price_key]:
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                elif change_ratio*(-1.0) >= high_low_threshhold:
                    hlpoint_map['change_price'].append(current_price)
                    hlpoint_map['change_date'].append(current_date)
                    hlpoint_map['change_ratio'].append((hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                    hlpoint_map_flag = 'down'
            elif hlpoint_map_flag == 'down':
                if current_price > stock_price_df.loc[index, price_key]:
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                elif change_ratio >= high_low_threshhold:
                    hlpoint_map['change_price'].append(current_price)
                    hlpoint_map['change_date'].append(current_date)
                    hlpoint_map['change_ratio'].append((hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
                    current_price = stock_price_df.loc[index, price_key]
                    current_date = index
                    hlpoint_map_flag = 'up'
    plt.ylabel(stock_code+'  '+stock_map['name'])
    plt.plot(stock_price_df.index, stock_price_df.close.values, marker = '.')
    plt.plot(stock_price_df.index, stock_price_df[price_key], marker = ',')
    # 布林带
    plt.plot(stock_price_df.index, stock_price_df['BOLL_UPPER'].values, 'k--')
    plt.plot(stock_price_df.index, stock_price_df['BOLL_MID'].values, 'k--')
    plt.plot(stock_price_df.index, stock_price_df['BOLL_LOWER'].values, 'k--')
    plt.plot(hlpoint_map['change_date'], hlpoint_map['change_price'], 'r^')
    for date,price,ratio in zip(hlpoint_map['change_date'], hlpoint_map['change_price'],hlpoint_map['change_ratio']):
        plt.text(date, price+3, '({},{},{}%)'.format(date.strftime("%Y-%m-%d"), np.round(price,3), round(ratio*100, 2)))
    plt.show()

# 执行---------------------------------------------------------------------
stock_plot(stock_code, high_low_threshhold, day_count)



