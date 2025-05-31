import math

import MyUtils;import time;
import MyTT;
from Ashare import *
stock_count=10000
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
    time.sleep(0.1)
    i = i + 1
    if i > stock_count:
        break
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_map['pe'] <= 0 or stock_map['pe'] > 15 or stock_map['total_market_value'] < 1000:
        continue
    print(stock_code, stock_map['name'], stock_map['pe'], '--------------------------------------------------------')
    print(stock_map)





