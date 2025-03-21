import pandas as pd

from Ashare import *
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
N日平均值
'''
def ma(S, n):
    return pd.Series(S).rolling(n).mean().values

'''
BIAS 乖离率
表示当前价格与某一周期移动平均线（MA）的百分比偏离程度，用于判断价格短期是否“过度上涨”或“过度下跌”。
一般n取6短期,12中期,24长期
'''
def bias(CLOSE, n):
    MA=pd.Series(CLOSE).rolling(n).mean().values
    return numpy.round((CLOSE-MA)/MA*100)


'''
RSI相对强弱指数（暂时无平均涨幅平滑处理，所以不准确）
动量振荡器，用于衡量股票或其他金融资产的价格变动速度和变化幅度，以判断超买或超卖状况。
70,30
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
衡量价格波动性和市场超买超卖状态，价格支撑位
'''
def boll(CLOSE, n=20, p=2):
    MA=pd.Series(CLOSE).rolling(n).mean().values
    STD=pd.Series(CLOSE).rolling(n).std(ddof=0).values
    UPPER = MA + STD * p
    LOWER = MA - STD * p
    return numpy.round(UPPER, 3), numpy.round(MA, 3), numpy.round(LOWER, 3)


'''
MACD 其实还是价格趋势的平滑，可以预示买点卖点
两条移动平均线的差异（DIF线）及其平滑线（DEA线）来反映价格的变化趋势，并结合柱状图（MACD Histogram）展示动量的强弱
'''
def macd(CLOSE, short=12, long=26, m=9):
    EMA_SHORT=pd.Series(CLOSE).ewm(span=short, adjust=False).mean().values
    EMA_LONG=pd.Series(CLOSE).ewm(span=long, adjust=False).mean().values
    DIF = EMA_SHORT - EMA_LONG  # 差异线
    DEA = pd.Series(DIF).ewm(span=m, adjust=False).mean().values  # 信号线
    MACD = 2 * (DIF - DEA)  #  直方图
    return numpy.round(DIF, 3), numpy.round(DEA, 3), numpy.round(MACD, 3)

'''
成交量加权VMACD，结合了交易量(使用效果不好，还不如MACD)
'''
def vmacd(CLOSE, VOLUME, short=12, long=26, m=9):
    VWAP = CLOSE * VOLUME
    EMA_SHORT = pd.Series(VWAP).ewm(span=short, adjust=False).mean().values/pd.Series(VOLUME).ewm(span=short, adjust=False).mean().values
    EMA_LONG = pd.Series(VWAP).ewm(span=long, adjust=False).mean().values/pd.Series(VOLUME).ewm(span=long, adjust=False).mean().values
    DIF = EMA_SHORT - EMA_LONG  # 差异线
    DEA = pd.Series(DIF).ewm(span=m, adjust=False).mean().values  # 信号线
    MACD = 2 * (DIF - DEA)  # 直方图
    return numpy.round(DIF, 3), numpy.round(DEA, 3), numpy.round(MACD, 3)

'''
KDJ
评估股票的超买和超卖状态，反应灵敏，适合短期交易
80，20
'''
def kdj(CLOSE,HIGH,LOW, n=9,m1=3,m2=3):
    LLV=pd.Series(LOW).rolling(n).min().values
    HHV=pd.Series(HIGH).rolling(n).max().values
    RSV=(CLOSE-LLV)/(HHV-LLV) * 100
    K=pd.Series(RSV).ewm(span=m1*2-1, adjust=False).mean().values
    D=pd.Series(K).ewm(span=m2*2-1, adjust=False).mean().values
    J=K*3-D*2
    return K,D,J

'''
ATR 价格波动幅度
反映市场短期内的价格波动剧烈程度，高波动性常伴随趋势行情，低波动性可能预示盘整
'''
def atr(CLOSE,HIGH,LOW, n=14):
    CLOSE_LASTDAY=pd.Series(CLOSE).shift(1).values
    TR = numpy.maximum(HIGH-LOW, numpy.abs(CLOSE_LASTDAY-HIGH), numpy.abs(CLOSE_LASTDAY-LOW))
    return pd.Series(TR).rolling(n).mean().values

'''
MFI 资金流量指数
资金流入流出强度
结合价格和成交量的震荡指标（0-100），类似于RSI（相对强弱指数），但加入了成交量数据，用于衡量资金流入流出的强度
MFI > 80为超买（可能回调），MFI < 20为超卖（可能反弹）
'''
def mfi(CLOSE,HIGH,LOW,VOLUME,n=14,m=6):
    TP=(CLOSE+HIGH+LOW)/3
    MF=TP * VOLUME
    MF_LASTDAY=pd.Series(MF).shift(1).values
    #SIG = numpy.round((MF - MF_LASTDAY) / numpy.abs(MF - MF_LASTDAY), 0)
    #FUNDIN = pd.Series(numpy.maximum(SIG,0) * MF).w.rolling(n).sum().values
    #FUNDOUT = pd.Series(numpy.abs(numpy.minimum(SIG,0)) * MF).rolling(n).sum().values

    FUNDIN = pd.Series(MF).where(MF >= MF_LASTDAY, 0).rolling(n).sum().values
    FUNDOUT = pd.Series(MF).where(MF < MF_LASTDAY, 0).rolling(n).sum().values

    MFI=100 - (100/(1+FUNDIN/FUNDOUT))
    MFIM=pd.Series(MFI).rolling(m).mean().values
    return numpy.round(MFIM, 3)
