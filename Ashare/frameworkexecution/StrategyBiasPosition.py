import numpy as np
from Ashare.frameworkexecution.StrategyDefault import StrategyDefault
import matplotlib
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import Ashare.MyUtils as myUtils

# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
# 负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
# 交互模式
plt.ion()

class StrategyBiasPosition(StrategyDefault):
    bias_percent_threshold = 25
    bias_key = 'BIAS30'

    def __init__(self):
        pass

    # 计算特定stock
    def analyze_one_stock(self, stock_code, stock_info_map, day_count):
        print('分析单个目标：', stock_code)
        is_filtered, stock_price_df = self.analyze_choose_stock(stock_code, stock_info_map, day_count)
        print('is_filtered:', is_filtered)
        return stock_price_df

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
                # 'min': round(min(data_list), 2),
                # 'max': round(max(data_list), 2),
                # 'mean': round(sum(data_list) / len(data_list), 2),
                'median': round(sorted(data_list)[len(data_list) // 2], 2),
                'current': round(current_data, 2),
                'percentile': percentile
            }
        if stats is None:
            return False, stock_price_df
        analysis_map = {
            'stock_code': stock_code,
            'stock_name': stock_info_map.get('name', ''),
            'stats': stats
        }
        stock_info_map['analysis_map'] = analysis_map
        is_filtered = (percentile <= self.bias_percent_threshold)
        return is_filtered, stock_price_df

    # 针对单个目标计算额外指标并绘图
    def plot_stock_data(self, stock_code, stock_detail_map, stock_price_df):
        price_key = 'close'
        plt.title(stock_detail_map['name'] + stock_code)
        # 绘制价格线
        plt.plot(stock_price_df.index, stock_price_df[price_key], marker=',')
        # 绘制均线
        plt.plot(stock_price_df.index, stock_price_df['MA30'].values, 'g-')
        plt.tight_layout()
        plt.show(block=True)
        return


#-----------------------------




