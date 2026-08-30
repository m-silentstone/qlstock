import numpy as np
import pandas as pd
import time
import json
import argparse
from fontTools.misc.cython import returns

from Ashare.frameworkexecution.StrategyDefault import StrategyDefault
from Ashare.frameworkexecution.StrategyPbPePosition import StrategyPbPePosition
from Ashare.frameworkexecution.StrategyBiasPosition import StrategyBiasPosition

#global_stock_code = 'sz000001'
# global_stock_code = None
# global_stock_history_data_days = 2000
# global_stock_code_index_start = 0
# global_stock_code_index_end = 9999
# global_stock_list_file = '../all_large_stocks_field.txt'
# strategyObj = StrategyBiasPosition()



class ExecutionFramework:
    #stock_code = None
    stock_code = 'sh600309'
    stock_history_data_days = 2000
    stock_code_index_start = 0
    stock_code_index_end = 9999
    stock_list_file = '../all_large_stocks_field.txt'
    holding_stocks = []
    strategyObj = StrategyBiasPosition()

    def __init__(self):
        pass

    # 在列表中挑选合适买入/卖出的股票
    def filter_choose_stocks(self):
        if self.stock_history_data_days is None:
            day_count = 1000
        else:
            day_count = self.stock_history_data_days
        if self.stock_code is not None:
            print('stock_code is not none...')
            return
            # stock_code = self.stock_code
            # # 分析PE和PB分位情况
            # result = analyze_pe_pb(stock_code, day_count)
            # # 打印分析结果
            # print_analysis_result(result)
        allstockcode_array = []
        filtered_stocks = {}
        with open(self.stock_list_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines[0:]:
                array = line.split()
                code_array = array[0].split('.')
                allstockcode_array.append(str(code_array[1] + code_array[0]).lower())
            stock_code_index = max(0, self.stock_code_index_start)
            while stock_code_index < len(allstockcode_array):
                if stock_code_index >= self.stock_code_index_end > 0:
                    break
                print('stock_code_index', stock_code_index)
                stock_code = allstockcode_array[stock_code_index]
                time.sleep(0.2)
                stock_info_map = self.strategyObj.get_stock_info_data(stock_code)
                # 基本信息过滤
                if not self.strategyObj.basic_filter_stock(stock_info_map):
                    stock_code_index = stock_code_index + 1
                    continue
                time.sleep(0.2)
                # 分析过程
                is_filtered, stock_detail_map, stock_price_df = self.strategyObj.analyze_choose_stock(stock_code, stock_info_map,
                                                                                 day_count)
                # 判断选入
                if not is_filtered:
                    stock_code_index = stock_code_index + 1
                    continue
                print('条件选入:', stock_code)
                print(stock_detail_map)
                self.strategyObj.print_sell_plan(stock_info_map)
                filtered_stocks[stock_code] = stock_detail_map
                stock_code_index = stock_code_index + 1
            # 打印分析结果
            print(f"{'=' * 60}")
            print(filtered_stocks)

    # 分析单个股票，包含绘图
    def analyze_one_stock(self):
        if self.stock_code is None or len(executionFramework.stock_code) <= 0:
            print('stock_code empty...')
            return
        if self.stock_history_data_days is None:
            day_count = 1000
        else:
            day_count = self.stock_history_data_days
        stock_info_map = self.strategyObj.get_stock_info_data(self.stock_code)
        is_filtered, stock_detail_map, stock_price_df = self.strategyObj.analyze_choose_stock(self.stock_code, stock_info_map, day_count)
        if stock_price_df is None:
            print('stock_price_df empty...')
            return
        self.strategyObj.print_sell_plan(stock_info_map)
        self.strategyObj.plot_stock_data(self.stock_code, stock_detail_map, stock_price_df)


    # 结合已持仓股票信息（code,持仓量, 买入价格, 持仓时间）确定是否要卖出
    def judge_stocks_sell(self):
        pass





if __name__ == '__main__':
    executionFramework = ExecutionFramework()
    if executionFramework.stock_code is not None and len(executionFramework.stock_code) > 0:
        executionFramework.analyze_one_stock()
    else:
        executionFramework.filter_choose_stocks()
