import math
import numpy
import MyUtils;import time;
import MyTT;
from Ashare import *

stock_count=1
day_count=2000
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
    i = i + 1
    if i> stock_count:
        break
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        break
    print(stock_code, stock_map['name'],'--------------------------------------------------------')
    #日线
    OPEN = stock_price_df.open.values
    CLOSE=stock_price_df.close.values
    HIGH=stock_price_df.high.values
    LOW=stock_price_df.low.values
    VOLUME=stock_price_df.volume.values

    highest = numpy.max(HIGH)
    lowest = numpy.min(LOW)
    distance = highest - lowest

    for index, row in stock_price_df.iterrows():
        # 分位
        stock_price_df.loc[index, 'status'] = numpy.round((row['close'] - lowest) / distance * 100, 3)

    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.precision', 3,
                           ):
        print(stock_price_df)
    print(stock_map)
    time.sleep(1)






