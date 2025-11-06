import math
import numpy as np
import MyUtils;import time;
import MyTT;

# 获取动量最高的ETF
def get_top_momentum_etf(etf_pool):
    scores = {etf: calculate_momentum(etf) for etf in etf_pool}
    print(scores)
    return max(scores, key=scores.get)

# 动量因子计算
def calculate_momentum(etf, days=25):
    stock_price_df = MyUtils.get_price_tx(etf, frequency='1d', count=days)
    closelist = stock_price_df['close'].values
    # print(etf,'-----------------')
    #print(closelist)
    y = np.log(closelist)
    x = np.arange(len(y))
    weights = np.linspace(1, 2, len(y))  # 线性增加权重
    slope, intercept = np.polyfit(x, y, 1, w=weights)
    annualized_return = math.exp(slope * 250) - 1
    residuals = y - (slope * x + intercept)
    r_squared = 1 - (np.sum(weights * residuals**2) / np.sum(weights * (y - np.mean(y))**2))
    return annualized_return * r_squared

ETF_POOL = [
    '518880.XSHG',  # 黄金ETF（大宗商品）
    '513100.XSHG',  # 纳指100（海外资产）
    '159915.XSHE',  # 创业板100（成长股）
    #'510180.XSHG',  # 上证180（价值股）
    '513880.XSHG',  # 日经225
    '513030.XSHG',  # 德国ETF
    '159980.XSHE',  # 有色金属
    '501018.XSHG',  # 原油
    '511090.XSHG',  # 国债
    '512890.XSHG',  # 红利低波（价值股）
    #'159985.XSHE',  # 豆粕
    #'164824.XSHE',  # 印度
    #'510170.XSHG',  # 额外：大宗商品ETF
    #'513180.XSHG',  # 额外：恒生科技ETF
    '513060.XSHG',  # 额外：恒生医疗ETF
]

print(time.strftime("------ %Y-%m-%d %H:%M:%S ------", time.localtime()))
print(get_top_momentum_etf(ETF_POOL))













