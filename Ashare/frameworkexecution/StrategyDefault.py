import numpy as np
import pandas as pd
import time
import requests
import json
import argparse
from fontTools.misc.cython import returns

class StrategyDefault:
    name = 'StrategyDefault'
    def __init__(self):
        pass
    # 计算特定stock
    def analyze_one_stock(self, stock_code):
        print(stock_code)

    # 股票筛选（包含筛选条件）True表示符合条件；False表示被排除
    def basic_filter_stock(self, stock_map):
        if 'pe' not in stock_map.keys() or 'total_market_value' not in stock_map.keys():
            return False
        if stock_map['total_market_value'] < 800:
            return False
        print(stock_map, '--------------------------------------------------------')
        return True

    # 股票分析和继续筛选 返回1：True表示符合条件；False表示被排除。返回2：股票详细信息
    def analyze_choose_stock(self, stock_code, stock_info_map, day_count):
        # 可替换的策略
        return False, None



# 公共方法--------------------------------------------------------------------------------------------------------
    def calculate_percentile(self, value, data_list):
        """
        计算值在数据列表中的百分位

        Args:
            value: 当前值
            data_list: 历史数据列表

        Returns:
            percentile: 百分位（0-100）
        """
        if not data_list or len(data_list) == 0:
            return None

        data_array = np.array(data_list)
        percentile = np.sum(data_array < value) / len(data_array) * 100
        return round(percentile, 2)