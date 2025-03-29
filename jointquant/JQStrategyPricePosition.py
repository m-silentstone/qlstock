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

    context.is_get_history = {}
    context.stocks_price_df = {}
    context.stocks_highest = {}
    context.stocks_lowest = {}

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
        if row['code'] in context.is_get_history:
            print(row['code'])
            stock_price_today = get_bars(row['code'], count=1, unit='1d',
                                         fields=['date', 'open', 'high', 'low', 'close', 'volume'])
            # print('stock_price_today:', stock_price_today)
            # print('context.stocks_highest[row[code]]:',context.stocks_highest[row['code']])
            # print('stock_price_today[high][-1]', stock_price_today['high'][-1])
            context.stocks_highest[row['code']] = numpy.maximum(stock_price_today['high'][-1],
                                                                context.stocks_highest[row['code']])
            context.stocks_lowest[row['code']] = numpy.minimum(stock_price_today['low'][-1],
                                                               context.stocks_lowest[row['code']])
            distance = context.stocks_highest[row['code']] - context.stocks_lowest[row['code']]
            position_today = numpy.round(
                (stock_price_today['close'][-1] - context.stocks_lowest[row['code']]) / distance * 100, 3)
            # 更新行情df
            stock_price_df = context.stocks_price_df[row['code']]
            # print('stock_price_df:',stock_price_df)
            # print('stock_price_today[date]:',stock_price_today['date'])
            # print('stock_price_today[date][-1]:',stock_price_today['date'][-1])
            # print('stock_price_df[DATE]:',stock_price_df['DATE'])
            # print('stock_price_df[CLOSE]:',stock_price_df['CLOSE'])
            # print('stock_price_df[HIGH]:',stock_price_df['HIGH'])
            # print('stock_price_df[LOW]:',stock_price_df['LOW'])

            stock_price_df['DATE'].append(stock_price_today['date'][-1])
            stock_price_df['CLOSE'].append(stock_price_today['close'][-1])
            stock_price_df['HIGH'].append(stock_price_today['high'][-1])
            stock_price_df['LOW'].append(stock_price_today['low'][-1])
            stock_price_df['VOLUME'].append(stock_price_today['volume'][-1])
            stock_price_df['POSITION'].append(position_today)

            # 保留最新的100个
            stock_price_df['DATE'] = stock_price_df['DATE'][-100:]
            stock_price_df['CLOSE'] = stock_price_df['CLOSE'][-100:]
            stock_price_df['HIGH'] = stock_price_df['HIGH'][-100:]
            stock_price_df['LOW'] = stock_price_df['LOW'][-100:]
            stock_price_df['VOLUME'] = stock_price_df['VOLUME'][-100:]
            stock_price_df['POSITION'] = stock_price_df['POSITION'][-100:]
            # print('stocks_price_df:', context.stocks_price_df[row['code']])
            # print('stocks_highest:', context.stocks_highest[row['code']])
            # print('stocks_lowest:', context.stocks_lowest[row['code']])
        else:
            print(row['code'])
            stock_price_array = get_bars(row['code'], count=2000, unit='1d',
                                         fields=['date', 'open', 'high', 'low', 'close', 'volume'])
            stock_price_df = {}
            stock_price_df['DATE'] = stock_price_array['date'].tolist()
            stock_price_df['CLOSE'] = stock_price_array['close'].tolist()
            stock_price_df['HIGH'] = stock_price_array['high'].tolist()
            stock_price_df['LOW'] = stock_price_array['low'].tolist()
            stock_price_df['VOLUME'] = stock_price_array['volume'].tolist()
            if len(stock_price_df['HIGH']) <= 0 or len(stock_price_df['LOW']) <= 0:
                continue
            context.stocks_highest[row['code']] = numpy.max(stock_price_df['HIGH'])
            context.stocks_lowest[row['code']] = numpy.min(stock_price_df['LOW'])
            distance = context.stocks_highest[row['code']] - context.stocks_lowest[row['code']]
            stock_price_df['POSITION'] = numpy.round(
                (pd.Series(stock_price_df['CLOSE']) - context.stocks_lowest[row['code']]) / distance * 100, 3).tolist()
            context.stocks_price_df[row['code']] = stock_price_df
            # print('stocks_price_df:', context.stocks_price_df[row['code']])
            # print('stocks_highest:', context.stocks_highest[row['code']])
            # print('stocks_lowest:', context.stocks_lowest[row['code']])
            context.is_get_history[row['code']] = True

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


def buy_check(code, stock_price_df, context):
    # 持有了就不再买了
    if context.portfolio.positions[code].closeable_amount > 0:
        return False

    if stock_price_df['POSITION'][-1] < 30:
        print(str(context.current_dt.date()) + ' ' + code + ' 分位值：' + str(
            stock_price_df['POSITION'][-1]) + ',小于分位阈值，买入')
        return True
    return False


def sell_check(code, stock_price_df, context):
    # 今日买入了就不卖出
    if context.portfolio.positions[code].today_amount > 0:
        return False
    # 不持有就不卖出
    if context.portfolio.positions[code].closeable_amount <= 0:
        return False
    if stock_price_df['POSITION'][-1] > 60:
        print(str(context.current_dt.date()) + ' ' + code + ' 分位值：' + str(
            stock_price_df['POSITION'][-1]) + ',大于分位阈值，卖出')
        return True
    return False










