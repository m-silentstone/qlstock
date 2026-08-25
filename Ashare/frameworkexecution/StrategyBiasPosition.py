import numpy as np
import pandas as pd
import time
import requests
import json
import argparse
from fontTools.misc.cython import returns
from Ashare.frameworkexecution.StrategyDefault import StrategyDefault
import Ashare.MyUtils as myUtils

class StrategyBiasPosition(StrategyDefault):
    bias_percent_threshold = 25
    bias_key = 'BIAS60'

    def __init__(self):
        pass

    # 股票分析和继续筛选 返回1：True表示符合条件；False表示被排除。返回2：股票详细信息
    def analyze_choose_stock(self, stock_code, stock_info_map, day_count):
        stock_price_df = myUtils.get_stock_price_data(stock_code)
        # 计算技术指标
        myUtils.calculate_indicators(stock_price_df)
        return self.filter_bias(stock_code, stock_info_map, stock_price_df)

    def filter_bias(self, stock_code, stock_info_map, stock_price_df):
        data_list = stock_price_df[self.bias_key].tolist()
        current_data = data_list[-1]
        data_list = [x for x in data_list if np.isnan(x) == False]
        percentile = None
        if len(data_list) > 0:
            percentile = self.calculate_percentile(current_data, data_list)
        # 获取统计信息
        stats = None
        if len(data_list) > 0:
            stats = {
                'min': round(min(data_list), 2),
                'max': round(max(data_list), 2),
                'mean': round(sum(data_list) / len(data_list), 2),
                'median': round(sorted(data_list)[len(data_list) // 2], 2),
                'current': round(current_data, 2),
                'percentile': percentile
            }
        if stats is None:
            return False, None
        analysis_map = {
            'stock_code': stock_code,
            'stock_name': stock_info_map.get('name', ''),
            'stats': stats
        }
        is_filtered = (percentile <= self.bias_percent_threshold)
        return is_filtered, analysis_map

#-----------------------------




