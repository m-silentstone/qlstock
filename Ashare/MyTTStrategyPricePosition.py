import math
import numpy
import MyUtils;import time;
import MyTT;
from Ashare import *

stock_code_index_end=-1
day_count=1999
stock_code_index_start = 0

#读A股全量股票文件
allstockcode_array=[]

high_pos_stocks=[]
low_pos_stocks=[]
high_pos_threshold=70
low_pos_threshold=30

pe_list=[]
pe_map_code={}
pe_map_name={}
pe_map_pos={}
pe_map_info={}
print(time.strftime("------ %Y-%m-%d %H:%M:%S ------", time.localtime()))
#with open('all_stocks_basic.txt', 'r', encoding='utf-8') as file:
with open('all_stocks_hk.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines[0:]:
        array=line.split()
        code_array=array[0].split('.')
        allstockcode_array.append(str(code_array[1]+code_array[0]).lower())

stock_code_index = stock_code_index_start
while stock_code_index < len(allstockcode_array):
    time.sleep(0.05)
    if 0 <= stock_code_index_end <= stock_code_index:
        break
    stock_code = allstockcode_array[stock_code_index]
    stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count)
    stock_map = MyUtils.get_from_gtime(stock_code)
    if len(stock_map) == 0:
        continue
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        break
    print(stock_code_index, stock_code, stock_map['name'],'--------------------------------------------------------')
    # 参考stock_map
    if stock_map['total_market_value'] < 500 or stock_map['pe'] <= 0:
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

    # 价格最高最低区间的百分位
    pos = numpy.round((stock_map['price'] - lowest) / distance * 100, 3)
    stock_map['pos'] = float(pos)

    # 收盘价格分位排序的百分位
    closes = CLOSE.tolist()
    close_today = closes[-1]
    length = len(closes)

    closes.sort()
    index1 = 1+closes.index(close_today)
    index2 = length - closes[::-1].index(close_today)
    pos1 = numpy.round(50*(index1+index2) / length, 3)
    stock_map['pos1'] = float(pos1)

    if pos1 > high_pos_threshold:
        str_append = stock_code + stock_map['name'] + str(pos1) + '当前价:' + str(stock_map['price'])
        print('pos1>high_pos_threshold:' + str_append)
        high_pos_stocks.append(str_append)
    if pos1 < low_pos_threshold:
        str_append = stock_code + stock_map['name'] + str(pos1) + '当前价:' + str(stock_map['price'])
        print('pos1<low_pos_threshold:' + str_append)
        low_pos_stocks.append(str_append)

    # pe排序
    pe_list.append(stock_map['pe'])
    if stock_map['pe'] not in pe_map_code.keys():
        pe_map_code[stock_map['pe']] = []
        pe_map_name[stock_map['pe']] = []
        pe_map_pos[stock_map['pe']] = []
        pe_map_info[stock_map['pe']] = []
    pe_map_code[stock_map['pe']].append(stock_map['code'])
    pe_map_name[stock_map['pe']].append(stock_map['name'])
    pe_map_pos[stock_map['pe']].append(stock_map['pos1'])
    pe_map_info[stock_map['pe']].append(stock_map)
    stock_code_index = stock_code_index + 1

print('-------------------')
pe_list = list(set(pe_list))
pe_list.sort()
for pe in pe_list:
    print('-----pe:', pe)
    pe_list_code = pe_map_code[pe]
    pe_list_name = pe_map_name[pe]
    pe_list_pos = pe_map_pos[pe]
    pe_list_info = pe_map_info[pe]
    for i in range(len(pe_list_code)):
        print('code:', pe_list_code[i])
        print('name:', pe_list_name[i])
        print('pos:', pe_list_pos[i])
        print('info:', pe_list_info[i])
print('-------------------------')
print('high_pos_stocks:', high_pos_stocks)
print('---')
print('low_pos_stocks:', low_pos_stocks)



#--------------------------------------------------------------
# with pd.option_context('display.max_rows', None,
#                        'display.max_columns', None,
#                        'display.precision', 3,
#                        ):
#     print(stock_price_df)


