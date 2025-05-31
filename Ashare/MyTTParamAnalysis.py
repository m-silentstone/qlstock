import math

import MyUtils;import time;
import MyTT;
from Ashare import *
stock_count=10000
stock_code_index_start = 2700
#读全量股票文件
allstockcode_array=[]
# with open('all_stocks_basic.txt', 'r', encoding='utf-8') as file:
with open('all_stocks_hk.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        array=line.split()
        code_array=array[0].split('.')
        allstockcode_array.append(str(code_array[1]+code_array[0]).lower())

stock_code_index = stock_code_index_start
while stock_code_index < len(allstockcode_array):
    time.sleep(0.1)
    print('stock_code_index:' + str(stock_code_index))
    if stock_code_index >= stock_count:
        break
    stock_code = allstockcode_array[stock_code_index];
    stock_map = MyUtils.get_from_gtime(stock_code)
    if 0 < stock_map['pe'] <= 15 and stock_map['total_market_value'] >= 1000:
        print(stock_code, stock_map['name'], stock_map['pe'], '--------------------------------------------------------')
        print(stock_map)
    stock_code_index = stock_code_index + 1
print('程序运行结束...')



