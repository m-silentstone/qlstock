import math

import MyUtils;import MyTT as mytt;import time;
from Ashare import *
stock_count=1
day_count=100
#读A股全量股票文件
allstockcode_array=[]
with open('all_stocks_basic.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines[1:]:
        array=line.split()
        code_array=array[1].split('.')
        allstockcode_array.append(str(code_array[1]+code_array[0]).lower())

i=0
for stock_code in allstockcode_array:
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        break
    print(stock_code, stock_map['name'],'--------------------------------------------------------')
    #日线
    CLOSE=stock_price_df.close.values
    MA5 = mytt.MA(CLOSE, 5)
    MA10 = mytt.MA(CLOSE, 10)
    MA20 = mytt.MA(CLOSE, 20)
    MA30 = mytt.MA(CLOSE, 30)
    stock_price_df['MA5']=MA5
    stock_price_df['MA10']=MA10
    stock_price_df['MA20']=MA20
    stock_price_df['MA30']=MA30

    # RSI相对强弱指数
    RSI24 = MyUtils.rsi(CLOSE, 24)
    stock_price_df['RSI24']=RSI24

    # 布林带
    BOLL_UPPER,BOLL_MID,BOLL_LOWER = MyUtils.boll(CLOSE)
    stock_price_df['BOLL_UPPER']=BOLL_UPPER
    stock_price_df['BOLL_MID']=BOLL_MID
    stock_price_df['BOLL_LOWER']=BOLL_LOWER


    for index, row in stock_price_df.iterrows():
        # 确定插针
        change=abs(float(row['close'])-float(row['open']))
        upline=float(row['high'])-max(float(row['close']),float(row['open']))
        downline = min(float(row['close']), float(row['open'])) - float(row['low'])
        stock_price_df.loc[index, 'status']=''
        if math.isnan(row['MA5']) or math.isnan(row['MA10']) or math.isnan(row['MA20']) or math.isnan(row['MA30']):
            continue
        if row['MA5'] > row['MA10'] > row['MA20'] > row['MA30']:
            stock_price_df.loc[index, 'status'] += 'Up,' #上涨状态
        if row['MA5'] < row['MA10'] < row['MA20'] < row['MA30']:
            stock_price_df.loc[index, 'status'] += 'Down,' #下跌状态
        if upline > change * 2 and upline/float(row['close']) > 0.03:
            stock_price_df.loc[index, 'status'] += 'TopSpin,' #上插针
        if downline > change * 2 and downline/float(row['close']) > 0.03:
            stock_price_df.loc[index, 'status'] += 'BlowSpin,' #下插针


    #print(stock_price_df)
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(stock_price_df)
    print(stock_map)
    time.sleep(1)
    i=i+1
    if i>stock_count:
        break





