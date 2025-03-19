# 导入函数库
from jqdata import *
import numpy


# 初始化函数，设定基准等等
def initialize(context):
    g.security = '000300.XSHG'
    # 设定操作股票作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    context.total_cash = context.portfolio.available_cash

    context.macd_best_atrplus = {}
    context.macd_best_atrmin = {}
    context.macd_date = {}
    context.macd_win_length = 4

    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5),
                   type='stock')

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security=g.security)
    # 开盘时运行
    run_daily(market_open, time='open', reference_security=g.security)
    # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security=g.security)


## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：' + str(context.current_dt.time()))

    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    # send_message('美好的一天~')

    # 要操作的股票：
    # g.security = '000001.XSHE'


## 开盘时运行函数
def market_open(context):
    log.info('函数运行时间(market_open):' + str(context.current_dt.time()))
    log.info('函数运行日期：', str(context.current_dt.date()))
    log.info('可用现金：', str(context.portfolio.available_cash))

    df = get_fundamentals(query(
        valuation.code, valuation.market_cap
    ).filter(
        valuation.market_cap > 1000
    ).order_by(
        # 按市值降序排列
        valuation.market_cap.desc()
    ).limit(
        # 最多返回几个
        1000
    ), date=str(context.current_dt.date()))

    buy_stocks = []
    sell_stocks = []

    for index, row in df.iterrows():
        stock_price_array = get_bars(row['code'], count=100, unit='1d',
                                     fields=['date', 'open', 'high', 'low', 'close', 'volume'])
        print(row['code'])
        stock_price_df = pd.DataFrame()
        DATE = stock_price_array['date']
        CLOSE = stock_price_array['close']
        HIGH = stock_price_array['high']
        LOW = stock_price_array['low']
        VOLUME = stock_price_array['volume']
        stock_price_df['DATE'] = DATE
        stock_price_df['CLOSE'] = CLOSE
        stock_price_df['HIGH'] = HIGH
        stock_price_df['LOW'] = LOW
        stock_price_df['VOLUME'] = VOLUME

        # 价格日线
        # MA5 = ma(CLOSE, 5)
        # MA10 = ma(CLOSE, 10)
        # MA20 = ma(CLOSE, 20)
        # MA30 = ma(CLOSE, 30)
        # stock_price_df['MA5']=MA5
        # stock_price_df['MA10']=MA10
        # stock_price_df['MA20']=MA20
        # stock_price_df['MA30']=MA30

        # 成交量日线
        VMA5 = ma(VOLUME, 5)
        VMA10 = ma(VOLUME, 10)
        # VMA20 = ma(VOLUME, 20)
        # VMA30 = ma(VOLUME, 30)
        stock_price_df['VMA5'] = VMA5
        stock_price_df['VMA10'] = VMA10
        # stock_price_df['VMA20']=VMA20
        # stock_price_df['VMA30']=VMA30

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


        # ATR
        ATR = atr(CLOSE, HIGH, LOW)
        stock_price_df['ATR'] = ATR

        statistics(row['code'], stock_price_df, context)

        if buy_check(row['code'], stock_price_df, context):
            buy_stocks.append(row['code'])
        if sell_check(row['code'], stock_price_df, context):
            sell_stocks.append(row['code'])
    if len(buy_stocks) > 0:
        per_cash = min(context.portfolio.available_cash / len(buy_stocks), context.total_cash / 10)
        for buy_code in buy_stocks:
            print(str(context.current_dt.date()) + ' ' + '买入：' + str(buy_code) + '，金额：' + str(per_cash))
            order_value(buy_code, per_cash)
    if len(sell_stocks) > 0:
        for sell_code in sell_stocks:
            updatedNum = 0
            print(str(context.current_dt.date()) + ' ' + '卖出：' + str(sell_code) + '，剩余股数：' + str(updatedNum))
            order_target(sell_code, updatedNum)


## 收盘后运行函数
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):' + str(context.current_dt.time())))
    # 得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：' + str(_trade))
    log.info('一天结束')
    log.info('##############################################################')


'''
------------------
自定义方法
'''


def statistics(code, stock_price_df, context):
    if len(stock_price_df.index) <= 26:
        return False
    if code not in context.macd_best_atrplus:
        context.macd_best_atrplus[code] = []
        context.macd_best_atrmin[code] = []
        context.macd_date[code] = []
    if (stock_price_df.at[stock_price_df.index[-1], 'MACD'] > 0 and \
        stock_price_df.at[stock_price_df.index[-2], 'MACD'] <= 0) or \
            (stock_price_df.at[stock_price_df.index[-1], 'MACD'] < 0 and \
             stock_price_df.at[stock_price_df.index[-2], 'MACD'] >= 0):
        atr_plus_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE'] + 1.2 * stock_price_df.at[
            stock_price_df.index[-1], 'ATR']
        atr_min_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE'] - 1.2 * stock_price_df.at[
            stock_price_df.index[-1], 'ATR']
        context.macd_best_atrplus[code].append(atr_plus_price)
        context.macd_best_atrmin[code].append(atr_min_price)
        context.macd_date[code].append(stock_price_df.at[stock_price_df.index[-1], 'DATE'])


def buy_check(code, stock_price_df, context):
    if len(stock_price_df.index) <= 26:
        return False
    # 持有了就不再买了
    if context.portfolio.positions[code].closeable_amount > 0:
        return False

    length = len(context.macd_best_atrplus[code])
    if length <= context.macd_win_length:
        return False

    today_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE']
    macd_code_price_max = max(context.macd_best_atrplus[code][length - context.macd_win_length - 1:-1])
    if today_price > macd_code_price_max:
        print('价格突破macd和atr界限，买入')
        return True
    # if stock_price_df.at[stock_price_df.index[-1], 'DATE'] == context.macd_date[code][-1]:
    #     print('买入检查：价格是macd交叉点，进一步检查')
    #     today_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE']
    #     macd_code_price_max=max(context.macd_best_atrplus[code][length-context.macd_win_length-1:-1])
    #     if today_price > macd_code_price_max:
    #         return True
    return False


def sell_check(code, stock_price_df, context):
    if len(stock_price_df.index) <= 26:
        return False
    # 今日买入了就不卖出
    if context.portfolio.positions[code].today_amount > 0:
        return False
    # 不持有就不卖出
    if context.portfolio.positions[code].closeable_amount <= 0:
        return False
    # # 止损
    # if (context.portfolio.positions[code].price - context.portfolio.positions[code].acc_avg_cost)/context.portfolio.positions[code].acc_avg_cost <= -0.12:
    #     print(str(context.current_dt.date())+" 止损卖："+code+"当前价："+str(context.portfolio.positions[code].price)+
    #     "，成本价："+str(context.portfolio.positions[code].acc_avg_cost))
    #     return True
    # # 盈利
    # if (context.portfolio.positions[code].price - context.portfolio.positions[code].acc_avg_cost)/context.portfolio.positions[code].acc_avg_cost >= 0.3:
    #     print(str(context.current_dt.date())+" 盈利卖："+code+"当前价："+str(context.portfolio.positions[code].price)+
    #     "，成本价："+str(context.portfolio.positions[code].acc_avg_cost))
    #     return True

    length = len(context.macd_best_atrplus[code])
    if length <= context.macd_win_length:
        return False

    today_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE']
    macd_code_price_min = min(context.macd_best_atrmin[code][length - context.macd_win_length - 1:-1])
    if today_price < macd_code_price_min:
        print(str(context.current_dt.date()) + ' ' + code + " MACD+ATR条件卖")
        return True

    # 考虑boll
    if stock_price_df.at[stock_price_df.index[-1], 'CLOSE'] < stock_price_df.at[
        stock_price_df.index[-1], 'BOLL_MID'] and \
            stock_price_df.at[stock_price_df.index[-2], 'CLOSE'] < stock_price_df.at[
        stock_price_df.index[-2], 'BOLL_MID'] and \
            stock_price_df.at[stock_price_df.index[-3], 'CLOSE'] >= stock_price_df.at[
        stock_price_df.index[-3], 'BOLL_MID']:
        print(str(context.current_dt.date()) + ' ' + code + " boll条件卖")
        return True

    # if stock_price_df.at[stock_price_df.index[-1], 'DATE'] == context.macd_date[code][-1]:
    #     print('卖出检查：价格是macd交叉点，进一步检查')
    #     today_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE']
    #     macd_code_price_min=min(context.macd_best_atrmin[code][length-context.macd_win_length-1:-1])
    #     if today_price < macd_code_price_min:
    #         return True
    return False

    # if stock_price_df.at[stock_price_df.index[-1], 'DATE'] == context.macd_date[code][-1]:
    #     print('卖出检查：价格是macd交叉点，进一步检查')
    #     n=3
    #     length=len(context.macd_best_atrplus[code])
    #     if length > n:
    #         today_price = stock_price_df.at[stock_price_df.index[-1], 'CLOSE']
    #         macd_code_price_max=max(context.macd_best_atrplus[code][length-n-1:-1])
    #         macd_code_price_min=min(context.macd_best_atrmin[code][length-n-1:-1])
    #         if today_price < macd_code_price_min:
    #             return True
    # return False


'''
N日平均值
'''


def ma(S, n):
    return pd.Series(S).rolling(n).mean().values


'''
布林带
'''


def boll(CLOSE, n=20, p=2):
    MA = pd.Series(CLOSE).rolling(n).mean().values
    STD = pd.Series(CLOSE).rolling(n).std(ddof=0).values
    UPPER = MA + STD * p
    LOWER = MA - STD * p
    return numpy.round(UPPER, 3), numpy.round(MA, 3), numpy.round(LOWER, 3)


'''
MACD
'''


def macd(CLOSE, short=12, long=26, m=9):
    EMA_SHORT = pd.Series(CLOSE).ewm(span=short, adjust=False).mean().values
    EMA_LONG = pd.Series(CLOSE).ewm(span=long, adjust=False).mean().values
    DIF = EMA_SHORT - EMA_LONG  # 差异线
    DEA = pd.Series(DIF).ewm(span=m, adjust=False).mean().values  # 信号线
    MACD = 2 * (DIF - DEA)  # 直方图
    return numpy.round(DIF, 3), numpy.round(DEA, 3), numpy.round(MACD, 3)

'''
成交量加权 vmacd
'''
def vmacd(CLOSE, VALUME, short=12, long=26, m=9):
    VWAP = CLOSE * VALUME
    EMA_SHORT = pd.Series(VWAP).ewm(span=short, adjust=False).mean().values/pd.Series(VALUME).ewm(span=short, adjust=False).mean().values
    EMA_LONG = pd.Series(VWAP).ewm(span=long, adjust=False).mean().values/pd.Series(VALUME).ewm(span=long, adjust=False).mean().values
    DIF = EMA_SHORT - EMA_LONG  # 差异线
    DEA = pd.Series(DIF).ewm(span=m, adjust=False).mean().values  # 信号线
    MACD = 2 * (DIF - DEA)  # 直方图
    return numpy.round(DIF, 3), numpy.round(DEA, 3), numpy.round(MACD, 3)



'''
ATR
'''


def atr(CLOSE, HIGH, LOW, n=14):
    CLOSE_LASTDAY = pd.Series(CLOSE).shift(1).values
    TR = numpy.maximum(HIGH - LOW, numpy.abs(CLOSE_LASTDAY - HIGH), numpy.abs(CLOSE_LASTDAY - LOW))
    return pd.Series(TR).rolling(n).mean().values








