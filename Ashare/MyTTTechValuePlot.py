import math

import matplotlib
import numpy as np
import pandas as pd

import MyUtils;import time
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import MyTT;
from Ashare import *

#global_stock_code = 'sh688008'
global_stock_code = None
high_low_threshold = 0.05
high_low_day_threshold = 5
global_day_count = 200
global_more_day_count = 60
global_enddate_date = None
global_stock_code_index_start = 4661
global_stock_code_index_end = 9999
global_stock_list_file = 'all_stocks_basic.txt'

# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
# 负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
# 交互模式
plt.ion()
global_price_key = 'close'


def get_stock_data(stock_code, day_count, more_day_count, need_filter):
    """
    获取股票历史数据
    
    Args:
        need_filter:
        stock_code: 股票代码
        day_count: 要获取的天数
        more_day_count: 额外获取的天数
    
    Returns:
        stock_map: 股票基本信息
        stock_price_df: 股票价格数据
    """
    stock_map = MyUtils.get_from_gtime(stock_code)
    if stock_code[2:] != stock_map['code']:
        print('数据有问题！')
        return None, None
    if need_filter:
        is_filtered = filter_stock(stock_map)
        if not is_filtered:
            return None, None
        else:
            print('符合筛选规则', stock_map['code'], stock_map['name'])
    round_days = 300
    enddate_str = time.strftime('%Y-%m-%d', time.localtime())  # 结果包含end_date的价格
    if global_enddate_date is not None:
        enddate_str = global_enddate_date
    stock_price_df = MyUtils.get_price_tx(stock_code, end_date=enddate_str, frequency='1d',
                                          count=np.minimum(round_days, day_count + more_day_count))
    
    remain_days = day_count + more_day_count - len(stock_price_df)
    while remain_days > 0:
        element_end_date = (stock_price_df.index[0] + pd.Timedelta(days=-1)).strftime('%Y-%m-%d')
        element_stock_price_df = MyUtils.get_price_tx(stock_code, end_date=element_end_date, frequency='1d',
                                                      count=np.minimum(round_days, remain_days))
        if element_stock_price_df is None or len(element_stock_price_df) == 0:
            break
        remain_days = remain_days - len(element_stock_price_df)
        stock_price_df = pd.concat([element_stock_price_df, stock_price_df])
        time.sleep(0.2)
    
    return stock_map, stock_price_df


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
    
    # 价格移动平均线
    stock_price_df['MA5'] = MyUtils.ma(CLOSE, 5)
    stock_price_df['MA10'] = MyUtils.ma(CLOSE, 10)
    stock_price_df['MA20'] = MyUtils.ma(CLOSE, 20)
    stock_price_df['MA30'] = MyUtils.ma(CLOSE, 30)
    stock_price_df['MA60'] = MyUtils.ma(CLOSE, 30)
    
    # 成交量移动平均线
    stock_price_df['VMA5'] = MyUtils.ma(VOLUME, 5)
    stock_price_df['VMA10'] = MyUtils.ma(VOLUME, 10)
    stock_price_df['VMA20'] = MyUtils.ma(VOLUME, 20)
    stock_price_df['VMA30'] = MyUtils.ma(VOLUME, 30)
    
    # 乖离率
    stock_price_df['BIAS6'] = MyUtils.bias(CLOSE, 6)
    stock_price_df['BIAS12'] = MyUtils.bias(CLOSE, 12)
    stock_price_df['BIAS24'] = MyUtils.bias(CLOSE, 24)
    
    # RSI相对强弱指数
    stock_price_df['RSI24'] = MyUtils.rsi(CLOSE, 24)
    
    # CCI 商品通道指数
    stock_price_df['CCI14'] = MyUtils.cci(CLOSE, HIGH, LOW)
    
    # DMA 移动平均线差
    DMA_DIF, DMA_DIFMA = MyUtils.dma(CLOSE)
    stock_price_df['DMA_DIF'] = DMA_DIF
    stock_price_df['DMA_DIFMA'] = DMA_DIFMA
    
    # WR 威廉指数
    stock_price_df['WR10'] = MyUtils.wr(CLOSE, HIGH, LOW, 10)
    stock_price_df['WR6'] = MyUtils.wr(CLOSE, HIGH, LOW, 6)
    
    # ENE-S
    ENE_UPPER, ENE_MID, ENE_LOWER = MyUtils.ene(CLOSE)
    stock_price_df['ENE_UPPER'] = ENE_UPPER
    stock_price_df['ENE_MID'] = ENE_MID
    stock_price_df['ENE_LOWER'] = ENE_LOWER
    
    # 布林带
    BOLL_UPPER, BOLL_MID, BOLL_LOWER = MyUtils.boll(CLOSE)
    stock_price_df['BOLL_UPPER'] = BOLL_UPPER
    stock_price_df['BOLL_MID'] = BOLL_MID
    stock_price_df['BOLL_LOWER'] = BOLL_LOWER
    
    # MACD
    DIF, DEA, MACD = MyUtils.macd(CLOSE)
    stock_price_df['DIF'] = DIF
    stock_price_df['DEA'] = DEA
    stock_price_df['MACD'] = MACD
    
    # VMACD
    VDIF, VDEA, VMACD = MyUtils.vmacd(CLOSE, VOLUME)
    stock_price_df['VDIF'] = VDIF
    stock_price_df['VDEA'] = VDEA
    stock_price_df['VMACD'] = VMACD
    
    # KDJ
    KDJ_K, KDJ_D, KDJ_J = MyUtils.kdj(CLOSE, HIGH, LOW)
    stock_price_df['KDJ_K'] = KDJ_K
    stock_price_df['KDJ_D'] = KDJ_D
    stock_price_df['KDJ_J'] = KDJ_J
    
    # ATR
    stock_price_df['ATR14'] = MyUtils.atr(CLOSE, HIGH, LOW, 14)
    
    # MFI
    stock_price_df['MFI'] = MyUtils.mfi(CLOSE, HIGH, LOW, VOLUME, 14)
    
    return stock_price_df


def calculate_trend_points(stock_code, stock_name, stock_price_df, high_low_threshold, price_key):
    """
    计算趋势高低点
    
    Args:
        stock_price_df: 股票价格数据
        high_low_threshold: 高低点阈值
        price_key: 价格键名
    
    Returns:
        hlpoint_map: 趋势高低点数据
    """
    hlpoint_map = {
        'code': stock_code,
        'name': stock_name,
        'change_price': [],
        'change_ratio': [],
        'change_day_length': [],
        'change_date': [],
        'up_ratio': [],
        'up_day_length': [],
        'down_ratio': [],
        'down_day_length': []
    }

    print('起始：', stock_price_df.index[0].strftime('%Y-%m-%d'), '结束日期', stock_price_df.index[-1].strftime('%Y-%m-%d'))
    
    # 初始化第一个点
    hlpoint_map['change_price'].append(stock_price_df.iloc[0][price_key])
    hlpoint_map['change_date'].append(stock_price_df.index[0])
    hlpoint_map['change_ratio'].append(0.0)
    hlpoint_map['change_day_length'].append(0)
    hlpoint_map['is_trend_change'] = False
    
    hlpoint_map['isup'] = None
    for index, row in stock_price_df.iterrows():
        # 趋势高低点
        change_day_length = int((index - hlpoint_map['change_date'][-1]) / pd.Timedelta(1, 'D'))
        change_ratio = (stock_price_df.loc[index, price_key] - hlpoint_map['change_price'][-1]) * 1.0 / hlpoint_map['change_price'][-1]
        if hlpoint_map['isup'] is None:
            if change_ratio > high_low_threshold and change_day_length >= high_low_day_threshold:
                hlpoint_map['isup'] = True
                hlpoint_map['change_price'].append(stock_price_df.loc[index, price_key])
                hlpoint_map['change_date'].append(index)
                hlpoint_map['change_ratio'].append(change_ratio)
                hlpoint_map['change_day_length'].append(change_day_length)
            elif change_ratio * (-1.0) > high_low_threshold and change_day_length >= high_low_day_threshold:
                hlpoint_map['isup'] = False
                hlpoint_map['change_price'].append(stock_price_df.loc[index, price_key])
                hlpoint_map['change_date'].append(index)
                hlpoint_map['change_ratio'].append(change_ratio)
                hlpoint_map['change_day_length'].append(change_day_length)
        else:
            if hlpoint_map['isup'] is True:
                if hlpoint_map['change_price'][-1] < stock_price_df.loc[index, price_key]:
                    hlpoint_map['change_price'][-1] = stock_price_df.loc[index, price_key]
                    hlpoint_map['change_date'][-1] = index
                    hlpoint_map['change_ratio'][-1] = (stock_price_df.loc[index, price_key] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2]
                    hlpoint_map['change_day_length'][-1] = int((index - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'D'))
                elif change_ratio * (-1.0) > high_low_threshold and change_day_length >= high_low_day_threshold:
                    # 记录并转向
                    hlpoint_map['change_price'].append(stock_price_df.loc[index, price_key])
                    hlpoint_map['change_date'].append(index)
                    hlpoint_map['change_ratio'].append(change_ratio)
                    hlpoint_map['change_day_length'].append(change_day_length)
                    hlpoint_map['isup'] = False
            elif hlpoint_map['isup'] is False:
                if hlpoint_map['change_price'][-1] > stock_price_df.loc[index, price_key]:
                    hlpoint_map['change_price'][-1] = stock_price_df.loc[index, price_key]
                    hlpoint_map['change_date'][-1] = index
                    hlpoint_map['change_ratio'][-1] = (stock_price_df.loc[index, price_key] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2]
                    hlpoint_map['change_day_length'][-1] = int((index - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'D'))
                elif change_ratio > high_low_threshold and change_day_length >= high_low_day_threshold:
                    # 记录并转向
                    hlpoint_map['change_price'].append(stock_price_df.loc[index, price_key])
                    hlpoint_map['change_date'].append(index)
                    hlpoint_map['change_ratio'].append(change_ratio)
                    hlpoint_map['change_day_length'].append(change_day_length)
                    hlpoint_map['isup'] = True

    # 添加最后一个点（[-1]是最新价格，[-2,-4,-6]和up趋势一致，[-3,-5,-7]和up趋势相反）有可能[-1]和[-2]是同一个点，一致性处理为了趋势在[-2]
    hlpoint_map['change_price'].append(stock_price_df.iloc[-1][price_key])
    hlpoint_map['change_date'].append(stock_price_df.index[-1])
    hlpoint_map['change_ratio'].append(
        (hlpoint_map['change_price'][-1] - hlpoint_map['change_price'][-2]) * 1.0 / hlpoint_map['change_price'][-2])
    hlpoint_map['change_day_length'].append(
        int((hlpoint_map['change_date'][-1] - hlpoint_map['change_date'][-2]) / pd.Timedelta(1, 'D')))
    for ratio,day_length in zip(hlpoint_map['change_ratio'], hlpoint_map['change_day_length']):
        if ratio > 0:
            hlpoint_map['up_ratio'].append(ratio)
            hlpoint_map['up_day_length'].append(day_length)
        elif ratio < 0 :
            hlpoint_map['down_ratio'].append(ratio)
            hlpoint_map['down_day_length'].append(day_length)
    print('【涨幅】均值：', round(np.mean(hlpoint_map['up_ratio']), 4), '中位数：', round(np.median(hlpoint_map['up_ratio']), 4))
    print('【涨幅持续时间】均值：', round(np.mean(hlpoint_map['up_day_length']), 1), '中位数：', round(np.median(hlpoint_map['up_day_length']), 1))
    print('【跌幅】均值：', round(np.mean(hlpoint_map['down_ratio']), 4), '中位数：', round(np.median(hlpoint_map['down_ratio']), 4))
    print('【跌幅持续时间】均值：', round(np.mean(hlpoint_map['down_day_length']), 1), '中位数：', round(np.median(hlpoint_map['down_day_length']), 1))
    if len(hlpoint_map['change_ratio']) <= 3:
        return
    isup = (hlpoint_map['change_ratio'][-2] > 0)
    print('isup?', isup)
    print('change_ratio list ready...')
    trendline_date1 = None
    trendline_date2 = hlpoint_map['change_date'][-3]
    trendline_price1 = None
    trendline_price2 = hlpoint_map['change_price'][-3]
    point_index = -5
    while point_index * -1 <= len(hlpoint_map['change_ratio']):
        if isup and hlpoint_map['change_price'][point_index] < trendline_price2:
            trendline_price1 = hlpoint_map['change_price'][point_index]
            trendline_date1 = hlpoint_map['change_date'][point_index]
            print('isup and trendline_price1 ready...')
            break
        elif not isup and hlpoint_map['change_price'][point_index] > trendline_price2:
            trendline_price1 = hlpoint_map['change_price'][point_index]
            trendline_date1 = hlpoint_map['change_date'][point_index]
            print('isdown and trendline_price1 ready...')
            break
        point_index = point_index - 2
    if trendline_price1 is not None and trendline_date1 is not None:
        print('trendline_price1 and trendline_date1 ready...')
        k = (trendline_price2 - trendline_price1) / (trendline_date2.value - trendline_date1.value)
        b = trendline_price1 - k * trendline_date1.value
        # 趋势线（123准则1：突破趋势线）
        price_diff = stock_price_df.iloc[-1][price_key] - (k * hlpoint_map['change_date'][-1].value + b)
        is_trend_change1 = (price_diff < 0 and isup) or (price_diff > 0 and not isup)
        print('rule1:', is_trend_change1)
        # 趋势线（123准则2：趋势中不再有更高点或更低点，或最新价格已回落至最高低点以内）
        leak_price_diff = hlpoint_map['change_price'][-2] - hlpoint_map['change_price'][-4]
        leak_price_diff_ration = abs(leak_price_diff / hlpoint_map['change_price'][-4])
        is_trend_change2_1 = isup and (leak_price_diff < 0 or (
                    leak_price_diff_ration < 0.05 and stock_price_df.iloc[-1][price_key] -
                    hlpoint_map['change_price'][-4] < 0))
        is_trend_change2_2 = (not isup) and (leak_price_diff > 0 or (
                    leak_price_diff_ration < 0.05 and stock_price_df.iloc[-1][price_key] -
                    hlpoint_map['change_price'][-4] > 0))
        is_trend_change2 = is_trend_change2_1 or is_trend_change2_2
        print('rule2:', is_trend_change2)
        # 趋势相反的极值线（123准则3：价格已突破原反向点。上升趋势时价格已低于上一低点或下降趋势时价格已高于上一高点）
        price_diff3 = stock_price_df.iloc[-1][price_key] - hlpoint_map['change_price'][-3]
        is_trend_change3 = (isup and price_diff3 < 0) or (not isup and price_diff3 > 0)
        print('rule3:', is_trend_change3)
        # plt.plot([trendline_date1, hlpoint_map['change_date'][-1]], [hlpoint_map['change_price'][-3], hlpoint_map['change_price'][-3]], 'k--')
        hlpoint_map['is_trend_change'] = is_trend_change1 and is_trend_change2
        if hlpoint_map['is_trend_change']:
            if hlpoint_map['isup'] is False:
                print('下跌趋势可能结束，符合123：', stock_code)
            else:
                print('上升趋势可能结束，符合123：', stock_code)
        else:
            print('不符合123：', stock_code)
    return hlpoint_map


def plot_trend(stock_price_df, hlpoint_map, price_key):
    """
    绘制趋势图
    
    Args:
        stock_price_df: 股票价格数据
        hlpoint_map: 趋势高低点数据
        price_key: 价格键名
    """
    plt.title("趋势点")
    plt.ylabel(f"{hlpoint_map['code']}  {hlpoint_map['name']}")

    # 绘制价格线
    plt.plot(stock_price_df.index, stock_price_df[price_key], marker=',')
    
    # # 绘制布林带
    # plt.plot(stock_price_df.index, stock_price_df['BOLL_UPPER'].values, 'k--')
    # plt.plot(stock_price_df.index, stock_price_df['BOLL_MID'].values, 'k--')
    # plt.plot(stock_price_df.index, stock_price_df['BOLL_LOWER'].values, 'k--')
    # 绘制均线
    plt.plot(stock_price_df.index, stock_price_df['MA60'].values, 'r-')
    # plt.plot(stock_price_df.index, stock_price_df['MA10'].values, 'g-')

    
    # 绘制趋势点
    plt.plot(hlpoint_map['change_date'], hlpoint_map['change_price'], 'r^')

    # 趋势线
    if len(hlpoint_map['change_ratio']) > 3:
        trendline_date1 = None
        trendline_date2 = hlpoint_map['change_date'][-3]
        trendline_price1 = None
        trendline_price2 = hlpoint_map['change_price'][-3]
        isup = hlpoint_map['change_ratio'][-2] > 0
        point_index = -5
        while point_index * -1 <= len(hlpoint_map['change_ratio']):
            if isup and hlpoint_map['change_price'][point_index] < trendline_price2:
                trendline_price1 = hlpoint_map['change_price'][point_index]
                trendline_date1 = hlpoint_map['change_date'][point_index]
                break
            elif not isup and hlpoint_map['change_price'][point_index] > trendline_price2:
                trendline_price1 = hlpoint_map['change_price'][point_index]
                trendline_date1 = hlpoint_map['change_date'][point_index]
                break
            point_index = point_index - 2
        if trendline_price1 is not None and trendline_date1 is not None:
            k = (trendline_price2 - trendline_price1) / (trendline_date2.value - trendline_date1.value)
            b = trendline_price1 - k * trendline_date1.value
            # 趋势线（123准则1）
            plt.plot([trendline_date1, hlpoint_map['change_date'][-1]], [trendline_price1, k * hlpoint_map['change_date'][-1].value + b], 'k--')
            # 趋势线（123准则2）
            plt.plot([trendline_date1, hlpoint_map['change_date'][-1]], [hlpoint_map['change_price'][-4], hlpoint_map['change_price'][-4]], 'k--')
            # 趋势相反的极值线（123准则3）
            plt.plot([trendline_date1, hlpoint_map['change_date'][-1]], [hlpoint_map['change_price'][-3], hlpoint_map['change_price'][-3]], 'k--')

    # 添加趋势点标注
    for date, price, ratio, daylength in zip(
        hlpoint_map['change_date'], 
        hlpoint_map['change_price'], 
        hlpoint_map['change_ratio'], 
        hlpoint_map['change_day_length']
    ):
        plt.text(
            date, 
            price*1.01,
            '({},{},{}%,{}days)'.format(date.strftime("%Y-%m-%d"), np.round(price, 3), round(ratio * 100, 2), daylength)
        )
    
    plt.tight_layout()
    plt.show(block=True)

def plot_statistics_hist(stock_price_df, hlpoint_map, price_key):
    plt.subplot(2, 1, 1)
    plt.title("价格变动率分位计数")
    plt.hist(hlpoint_map['change_ratio'], bins=30)
    plt.subplot(2, 1, 2)
    plt.title("持续天数分位计数")
    plt.hist(hlpoint_map['change_day_length'], bins=30)
    plt.suptitle('股票价格图组')
    plt.show(block=True)


def stock_points_calc(stock_code, high_low_threshold, day_count, need_filtered = True):
    """
    绘制股票趋势图
    
    Args:
        need_filtered:
        stock_code: 股票代码
        high_low_threshold: 高低点阈值
        day_count: 要分析的天数
    """
    if day_count < 2:
        print('计算历史时间太短！')
        return None, None
    stock_map, stock_price_df = get_stock_data(stock_code, day_count, global_more_day_count, need_filtered)
    time.sleep(0.1)
    if stock_map is None or stock_price_df is None:
        return None, None
    print(stock_code, stock_map['name'], '--------------------------------------------------------')
    # 计算技术指标
    stock_price_df = calculate_indicators(stock_price_df)
    # 计算趋势高低点
    stock_price_df = stock_price_df[global_more_day_count:]
    print('数据长度:', len(stock_price_df))
    hlpoint_map = calculate_trend_points(stock_code, stock_map['name'], stock_price_df, high_low_threshold, global_price_key)
    return hlpoint_map, stock_price_df

def filter_stock(stock_map):
    if 'pe' not in stock_map.keys() or 'total_market_value' not in stock_map.keys():
        return False
    if stock_map['total_market_value'] < 800:
        return False
    print(stock_map, '--------------------------------------------------------')
    return True

def scan_stocks():
    if global_day_count < 2:
        print('计算历史时间太短！')
        return
    allstockcode_array = []
    stock_score_map = {}
    with open(global_stock_list_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines[0:]:
            array = line.split()
            code_array = array[0].split('.')
            allstockcode_array.append(str(code_array[1] + code_array[0]).lower())
        stock_code_index = max(0, global_stock_code_index_start)
        while stock_code_index < len(allstockcode_array):
            if global_stock_code_index_end > 0 and stock_code_index >= global_stock_code_index_end:
                break
            print('stock_code_index:' + str(stock_code_index))
            stock_code = allstockcode_array[stock_code_index];
            hlpoint_map, stock_price_df = stock_points_calc(stock_code, high_low_threshold, global_day_count)
            if hlpoint_map is not None and hlpoint_map['is_trend_change']:
                # 绘制趋势图
                plot_trend(stock_price_df, hlpoint_map, global_price_key)
                # 分位数绘图
                # plot_statistics_hist(stock_price_df, hlpoint_map, stock_code, stock_map['name'], price_key)
                break
            stock_code_index = stock_code_index + 1

def specific_stock_calc(stock_code):
    hlpoint_map, stock_price_df = stock_points_calc(stock_code, high_low_threshold, global_day_count, False)
    # 绘制趋势图
    plot_trend(stock_price_df, hlpoint_map, global_price_key)
    # 分位数绘图
    # plot_statistics_hist(stock_price_df, stock_map['name'], price_key)

def stock_calc_execute():
    if global_stock_code is None:
        scan_stocks()
    else:
        specific_stock_calc(global_stock_code)

# 执行---------------------------------------------------------------------
stock_calc_execute()
print(matplotlib.pyplot.isinteractive())


