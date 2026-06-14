import math

import MyUtils;import time;
stock_count=10000
stock_code_index_start = 0
check_stock_codes=[] #如果有元素，则只查询这些股票，不再遍历文件

allstockcode_array=[]
if len(check_stock_codes) > 0:
    for check_stock_code in check_stock_codes:
        time.sleep(0.1)
        stock_map = MyUtils.get_from_gtime(check_stock_code)
        if 'pe' not in stock_map.keys() or 'name' not in stock_map.keys():
            continue
        print(check_stock_code, stock_map['name'], stock_map['pe'], '--------------------------------------------------------')
        print(stock_map)
    print('程序运行结束...')
    exit(0)

# 读全量股票文件
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
    if 0 < stock_count <= stock_code_index:
        break
    stock_code = allstockcode_array[stock_code_index];
    stock_map = MyUtils.get_from_gtime(stock_code)
    if 0 < stock_map['pe'] <= 15 and stock_map['total_market_value'] >= 800:
        print(stock_code, stock_map['name'], stock_map['pe'], '--------------------------------------------------------')
        print(stock_map)
    stock_code_index = stock_code_index + 1
print('程序运行结束...')



