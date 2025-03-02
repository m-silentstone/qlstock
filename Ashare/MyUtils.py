from Ashare import *
import MyTT
import numpy

def get_price_tx(code, end_date='', count=10, frequency='1d', fields=[]):  # 明确调用腾讯接口
    xcode = code.replace('.XSHG', '').replace('.XSHE', '')  # 证券代码编码兼容处理
    xcode = 'sh' + xcode if ('XSHG' in code) else 'sz' + xcode if ('XSHE' in code) else code

    if frequency in ['1d', '1w', '1M']:  # 1d日线  1w周线  1M月线
        return get_price_day_tx(xcode, end_date=end_date, count=count,
                                frequency=frequency)

    if frequency in ['1m', '5m', '15m', '30m', '60m']:  # 分钟线 ,1m只有腾讯接口  5分钟5m   60分钟60m
        if frequency in '1m': return get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)
        return get_price_day_tx(xcode, end_date=end_date, count=count,
                                frequency=frequency)


def get_from_gtime(code):
    URL = f'https://qt.gtimg.cn/q={code}'
    is_hk=False
    switch_hand_percent_index=38
    if code[:2] == 'hk':
        is_hk=True
        switch_hand_percent_index=59

    str = requests.get(URL).content
    str = str.decode('GBK')
    array = str.split('~')
    map= {'name': array[1],
             'code': array[2],
             'price': array[3],
             'yesterday_close': array[4],
             'open': array[5],
             'volume_hands': array[6], #成交量（手数）
             'time': array[30],
             'updown': array[31], #涨幅
             'updown_percent': array[32], #涨幅比率
             'high': array[33],
             'low': array[34],
             'volume_10k': array[37], #成交量（万）
             'switch_hand_percent': array[switch_hand_percent_index], #换手率
             'swing': array[43], # 振幅
             'circulation_market_value': array[44], #流通市值
             'total_market_value': array[45]#总市值
             }
    if not is_hk:
        map['pb'] = array[46] #市净率
        map['pe'] = array[39] #市盈率
    return map

'''
RSI相对强弱指数（暂时无平均涨幅平滑处理，所以不准确）
'''
def rsi(CLOSE, n=24):
    CLOSE_LASTDAY=pd.Series(CLOSE).shift(1).values
    DIF_RATIO = (CLOSE - CLOSE_LASTDAY) / CLOSE_LASTDAY
    UP_RATIO=pd.Series(numpy.maximum(DIF_RATIO,0)).rolling(n).mean().values
    DOWN_RATIO=numpy.abs(pd.Series(numpy.minimum(DIF_RATIO,0)).rolling(n).mean().values)
    RS=UP_RATIO/DOWN_RATIO
    return numpy.round(100-(100/(1+RS)), 3)

'''
布林带
'''
def boll(CLOSE, n=20, p=2):
    MA=pd.Series(CLOSE).rolling(n).mean().values
    STD=pd.Series(CLOSE).rolling(n).std(ddof=0).values
    UPPER = MA + STD * p
    LOWER = MA - STD * p
    return numpy.round(UPPER, 3), numpy.round(MA, 3), numpy.round(LOWER, 3)