import math
import numpy
import MyUtils;import time;
import MyTT;
from Ashare import *

stock_code_index_end=1000
day_count=1000
stock_code_index_start = 0

#读A股全量股票文件
allstockcode_array=[]

high_pos_stocks=[]
low_pos_stocks=[]
high_pos_threshold=70
low_pos_threshold=30

with open('all_stocks_hk.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines[0:]:
        array=line.split()
        code_array=array[0].split('.')
        allstockcode_array.append(str(code_array[1]+code_array[0]).lower())

stock_code_index = stock_code_index_start
while stock_code_index < len(allstockcode_array):
    time.sleep(0.1)
    if 0 <= stock_code_index_end <= stock_code_index:
        break
    stock_code = allstockcode_array[stock_code_index]
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        break
    print(stock_code_index, stock_code, stock_map['name'],'--------------------------------------------------------')
    # 参考stock_map
    if stock_map['total_market_value'] < 800:
        stock_code_index = stock_code_index + 1
        continue
    print(stock_code_index, stock_code, stock_map['name'],'--------------------------------------------------------')

    #日线
    OPEN = stock_price_df.open.values
    CLOSE=stock_price_df.close.values
    HIGH=stock_price_df.high.values
    LOW=stock_price_df.low.values
    VOLUME=stock_price_df.volume.values

    highest = numpy.max(HIGH)
    lowest = numpy.min(LOW)
    distance = highest - lowest

    pos = numpy.round((stock_map['price'] - lowest) / distance * 100, 3)
    stock_map['pos'] = float(pos)
    if pos > high_pos_threshold:
        str_append = stock_code + stock_map['name'] + str(pos) + '当前价:' + str(stock_map['price'])
        print('pos>high_pos_threshold:' + str_append)
        high_pos_stocks.append(str_append)
    if pos < low_pos_threshold:
        str_append = stock_code + stock_map['name'] + str(pos) + '当前价:' + str(stock_map['price'])
        print('pos<low_pos_threshold:' + str_append)
        low_pos_stocks.append(str_append)
    print(stock_map)
    stock_code_index = stock_code_index + 1

print('-------------------')
print('high_pos_stocks:', high_pos_stocks)
print('---')
print('low_pos_stocks:', low_pos_stocks)



#--------------------------------------------------------------
# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     print(stock_price_df)


