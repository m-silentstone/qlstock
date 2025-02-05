from  Ashare import *

# 证券代码兼容多种格式 通达信，同花顺，聚宽
# sh000001 (000001.XSHG)    sz399006 (399006.XSHE)   sh600519 ( 600519.XSHG )

tax_ratio=0.9999
fund=10000
stock=0
count=1000
#df = get_price('sh000001', frequency='1d', count=count)  # 上证指数日线行情
df = get_price('sh000300', frequency='1d', count=count)  # 日线行情

print('上证指数日线行情\n',df)


'''
#每日按收盘价买入/卖出循环操作
for index, row in df.iterrows():
    print(index)
    print("close:",row['close'])
    if fund > 0:
        stock = fund/row['close']*tax_ratio
        print("stock:", stock)
        fund = 0
    else:
        fund = stock*row['close']*tax_ratio
        print("fund:", fund)

'''

#按定投天数平均分配金额，按收盘价买入
day_fund=fund/count
stock=0
for index, row in df.iterrows():
    print(index)
    print("close:",row['close'])
    stock+=day_fund/row['close']*tax_ratio
    print("stock:", stock, ",stock_fund:", stock*row['close']*tax_ratio)



