import math

from pandas.core.interchange.dataframe_protocol import DataFrame

import MyUtils;import time;
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import MyTT;
from Ashare import *
stock_count=1
day_count=150
plot_code='sz000001'
plot_df = None

#读A股全量股票文件
allstockcode_array=[]
with open('all_stocks_basic.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines[0:]:
        array=line.split()
        code_array=array[0].split('.')
        allstockcode_array.append(str(code_array[1]+code_array[0]).lower())

i=0
for stock_code in allstockcode_array:
    i = i + 1
    if i> stock_count:
        break
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count+30)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        break
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

    for index, row in stock_price_df.iterrows():
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


    #print(stock_price_df)
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(stock_price_df)
    print(stock_map)
    if stock_code == plot_code:
        plot_df = stock_price_df
    time.sleep(1)



# def buy_check(code, stock_price_df):
#
#
#
#
#
# def sell_check(code, stock_price_df, stockHoldInfo):
#     hold_info.positions[code].closeable_amount

# 绘图------------------------------------------------
if plot_df is not None:
    plt.ylabel(plot_code)
    plt.plot(plot_df.index, plot_df.close.values, marker = '.')
    # 布林带
    plt.plot(plot_df.index, plot_df['BOLL_UPPER'].values, 'r-')
    plt.plot(plot_df.index, plot_df['BOLL_MID'].values, 'r-')
    plt.plot(plot_df.index, plot_df['BOLL_LOWER'].values, 'r-')
    plt.show()

