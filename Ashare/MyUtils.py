from Ashare import *

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