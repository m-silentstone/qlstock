import MyUtils
from Ashare import *

# 证券代码兼容多种格式 通达信，同花顺，聚宽
# sh000001 (000001.XSHG)    sz399006 (399006.XSHE)   sh600519 ( 600519.XSHG )


#x日线计算
x=5
print(x,"日线计算和验证:")

df = MyUtils.get_price_tx('hk00700', frequency='1d', count=x)
i=0
result=0
while i < x:
    result += df.loc[df.index[i], 'close']
    i=i+1
print(df.index[0],"收盘5日线：",result/x)





tax_ratio=0.9999
fund=10000
stock=0
count=250
#df = get_price('sh000001', frequency='1d', count=count)  # 上证指数日线行情
#df = get_price('sh000300', frequency='1d', count=count)  # 沪深300日线行情
#df = get_price('sh518880', frequency='1d', count=count)  # 黄金ETF日线行情
#df = MyUtils.get_price_tx('sh518880', frequency='1d', count=count)  # 黄金ETF日线行情(腾讯接口)

df = MyUtils.get_price_tx('hk00700', frequency='1d', count=count)  # 腾讯日线行情(腾讯接口)

print('日线行情\n',df)


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

'''
#按定投天数平均分配金额，按收盘价买入
day_fund=fund/count
stock=0
for index, row in df.iterrows():
    print(index)
    print("close:",row['close'])
    stock+=day_fund/row['close']*tax_ratio
    print("stock:", stock, ",stock_fund:", stock*row['close']*tax_ratio)
'''

#第一天买入不动，最后一天卖出
print(df.index[0],"收盘价：",df.loc[df.index[0],'close'])
print(df.index[count-1],"收盘价：",df.loc[df.index[count-1],'close'])
stock=fund/df.loc[df.index[0],'close']*tax_ratio
print("stock:", stock, ",stock_fund:", stock*df.loc[df.index[count-1],'close']*tax_ratio)




