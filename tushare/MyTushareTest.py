import tushare as ts
import pandas as pd

my_token='c5b01e30303907647a3dd1724593954f9c90a637bde2f160df5e845a'

ts.set_token(my_token)
pro = ts.pro_api()

#查询当前所有正常上市交易的股票列表
#df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

#获取某一日某个交易所的全部股票
df = pro.hk_daily_adj(trade_date='20250213')

#df = pro.daily(ts_code='000001.SZ', start_date='20180701', end_date='20180718')
#df = pro.daily(trade_date='20250212')



with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
    print(df)
