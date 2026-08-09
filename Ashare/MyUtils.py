from ctypes.wintypes import SMALL_RECT
import pandas as pd
import numpy as np
import time
from Ashare import *
import numpy

global_day_count = 200
global_more_day_count = 60
global_enddate_date = None

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
    switch_hand_percent_index = 38
    if code[:2] == 'hk':
        is_hk=True
        switch_hand_percent_index=59
    str = requests.get(URL).content
    str = str.decode('GBK')
    array = str.split('~')
    if len(array) <= 45:
        map = {}
        return map
    map= {'name': array[1],
             'code': array[2], #代码
             'price': float(array[3].strip()) if len(array[3].strip())>0 else 0.00, #当前价
             'yesterday_close': float(array[4]), #昨日收盘价
             'open': float(array[5].strip()) if len(array[5].strip())>0 else 0.00, #当日开盘价
             'volume_hands': float(array[6].strip()) if len(array[6].strip())>0 else 0.00, #成交量（手数）
             'time': array[30], #数据时间
             'updown': float(array[31].strip()) if len(array[31].strip())>0 else 0.00, #涨幅
             'updown_percent': float(array[32].strip()) if len(array[32].strip())>0 else 0.00, #涨幅比率
             'high': float(array[33].strip()) if len(array[33].strip())>0 else 0.00, #当日最高价
             'low': float(array[34].strip()) if len(array[34].strip())>0 else 0.00, #当日最低价
             'volume_10k': float(array[37].strip()) if len(array[37].strip())>0 else 0.00, #成交量（万）
             'pe': float(array[39].strip()) if len(array[39].strip())>0 else 0.00, #市盈率
             'switch_hand_percent': array[switch_hand_percent_index], #换手率
             'swing': array[43], # 振幅
             'circulation_market_value': float(array[44].strip()) if len(array[44].strip())>0 else 0.00, #流通市值（亿元）
             'total_market_value': float(array[45].strip()) if len(array[45].strip())>0 else 0.00 #总市值（亿元）
             }
    if not is_hk:
        map['pb'] = float(array[46].strip()) if len(array[46].strip())>0 else 0.00 #市净率
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
CCI 商品通道指数
'''
def cci(CLOSE, HIGH, LOW, n=14):
    TP=(HIGH+LOW+CLOSE)/3
    SMA=pd.Series(TP).rolling(n).mean().values
    MD = pd.Series(TP).rolling(n).apply(lambda x: (numpy.abs(x - x.mean())).mean()).values
    return (TP-SMA)/(0.015*MD)


'''
WR 威廉指标
'''
def wr(CLOSE, HIGH, LOW, n):
    MAX = pd.Series(HIGH).rolling(n).max().values
    MIN = pd.Series(LOW).rolling(n).min().values
    WR = (MAX-CLOSE) / (MAX-MIN) * 100
    return numpy.round(WR, 3)

'''
DMA 移动平均线差
'''
def dma(CLOSE, n1=10, n2=50, m=10):
    DIF = pd.Series(CLOSE).rolling(n1).mean().values - pd.Series(CLOSE).rolling(n2).mean().values
    DIFMA = pd.Series(DIF).rolling(m).mean().values
    return DIF,DIFMA

'''
SAR 抛物转向指标，Stop and Reverse
'''


'''
ene-s 
'''
def ene(CLOSE, n=25, m1=6, m2=6):
    MA = pd.Series(CLOSE).rolling(n).mean().values
    MAH = MA * (1+m1/100)
    MAL = MA * (1-m2/100)
    return MAH, MA, MAL

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

# 获取股票基本信息
def get_stock_info_data(stock_code):
    stock_map = get_from_gtime(stock_code)
    if stock_map is None or len(stock_map) == 0 or stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        return None
    return stock_map

# 计算历史价格
def get_stock_price_data(stock_code):
    round_days = 250
    enddate_str = time.strftime('%Y-%m-%d', time.localtime())  # 结果包含end_date的价格
    if global_enddate_date is not None:
        enddate_str = global_enddate_date
    stock_price_df = get_price_tx(stock_code, end_date=enddate_str, frequency='1d',
                                          count=np.minimum(round_days, global_day_count + global_more_day_count))
    remain_days = global_day_count + global_more_day_count - len(stock_price_df)
    while remain_days > 0:
        element_end_date = (stock_price_df.index[0] + pd.Timedelta(days=-1)).strftime('%Y-%m-%d')
        element_stock_price_df = get_price_tx(stock_code, end_date=element_end_date, frequency='1d',
                                                      count=np.minimum(round_days, remain_days))
        if element_stock_price_df is None or len(element_stock_price_df) == 0:
            break
        remain_days = remain_days - len(element_stock_price_df)
        stock_price_df = pd.concat([element_stock_price_df, stock_price_df])
        time.sleep(0.1)
    return stock_price_df

# 计算各种技术指标
def calculate_indicators(stock_price_df):
    """
    计算各种技术指标

    Args:
        stock_price_df: 股票价格数据

    Returns:
        stock_price_df: 添加了技术指标的股票价格数据
    """
    # 提取基础数据到数组，减少重复访问DataFrame
    CLOSE = stock_price_df.close.values
    HIGH = stock_price_df.high.values
    LOW = stock_price_df.low.values
    VOLUME = stock_price_df.volume.values

    # 价格移动平均线（不复权）
    stock_price_df['MA5'] = ma(CLOSE, 5)
    stock_price_df['MA10'] = ma(CLOSE, 10)
    stock_price_df['MA20'] = ma(CLOSE, 20)
    stock_price_df['MA30'] = ma(CLOSE, 30)
    stock_price_df['MA60'] = ma(CLOSE, 60)

    # 成交量移动平均线
    stock_price_df['VMA5'] = ma(VOLUME, 5)
    stock_price_df['VMA10'] = ma(VOLUME, 10)
    stock_price_df['VMA20'] = ma(VOLUME, 20)
    stock_price_df['VMA30'] = ma(VOLUME, 30)

    # 乖离率
    stock_price_df['BIAS6'] = bias(CLOSE, 6)
    stock_price_df['BIAS12'] = bias(CLOSE, 12)
    stock_price_df['BIAS24'] = bias(CLOSE, 24)
    stock_price_df['BIAS30'] = bias(CLOSE, 30)

    # RSI相对强弱指数
    stock_price_df['RSI24'] = rsi(CLOSE, 24)

    # CCI 商品通道指数
    stock_price_df['CCI14'] = cci(CLOSE, HIGH, LOW)

    # DMA 移动平均线差
    DMA_DIF, DMA_DIFMA = dma(CLOSE)
    stock_price_df['DMA_DIF'] = DMA_DIF
    stock_price_df['DMA_DIFMA'] = DMA_DIFMA

    # WR 威廉指数
    stock_price_df['WR10'] = wr(CLOSE, HIGH, LOW, 10)
    stock_price_df['WR6'] = wr(CLOSE, HIGH, LOW, 6)

    # ENE-S
    ENE_UPPER, ENE_MID, ENE_LOWER = ene(CLOSE)
    stock_price_df['ENE_UPPER'] = ENE_UPPER
    stock_price_df['ENE_MID'] = ENE_MID
    stock_price_df['ENE_LOWER'] = ENE_LOWER

    # 布林带
    BOLL_UPPER, BOLL_MID, BOLL_LOWER = boll(CLOSE)
    stock_price_df['BOLL_UPPER'] = BOLL_UPPER
    stock_price_df['BOLL_MID'] = BOLL_MID
    stock_price_df['BOLL_LOWER'] = BOLL_LOWER

    # MACD
    DIF, DEA, MACD = macd(CLOSE)
    stock_price_df['DIF'] = DIF
    stock_price_df['DEA'] = DEA
    stock_price_df['MACD'] = MACD

    # VMACD
    VDIF, VDEA, VMACD = vmacd(CLOSE, VOLUME)
    stock_price_df['VDIF'] = VDIF
    stock_price_df['VDEA'] = VDEA
    stock_price_df['VMACD'] = VMACD

    # KDJ
    KDJ_K, KDJ_D, KDJ_J = kdj(CLOSE, HIGH, LOW)
    stock_price_df['KDJ_K'] = KDJ_K
    stock_price_df['KDJ_D'] = KDJ_D
    stock_price_df['KDJ_J'] = KDJ_J

    # ATR
    stock_price_df['ATR14'] = atr(CLOSE, HIGH, LOW, 14)

    # MFI
    stock_price_df['MFI'] = mfi(CLOSE, HIGH, LOW, VOLUME, 14)

    stock_price_df = stock_price_df[global_more_day_count:]
    return stock_price_df