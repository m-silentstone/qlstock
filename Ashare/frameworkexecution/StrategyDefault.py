import numpy as np
import matplotlib
import matplotlib.pyplot as plt ;from matplotlib.ticker import MultipleLocator
import Ashare.MyUtils as myUtils

# 中文字体为黑体
matplotlib.rcParams['font.family'] = 'SimHei'
# 负号显示
matplotlib.rcParams['axes.unicode_minus'] = False
# 交互模式
plt.ion()

class StrategyDefault:
    name = 'StrategyDefault'
    def __init__(self):
        pass
    # 计算特定stock
    def analyze_one_stock(self, stock_code, stock_info_map, day_count):
        print('分析单个目标：', stock_code)
        # 可替换的策略
        stock_price_df = myUtils.get_stock_price_data(stock_code)
        return stock_price_df

    def get_stock_info_data(self, stock_code):
        return myUtils.get_stock_info_data(stock_code)

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
        stock_price_df = myUtils.get_stock_price_data(stock_code)
        return False, stock_price_df

    # 针对单个目标计算额外指标并绘图
    def plot_stock_data(self, stock_code, stock_detail_map, stock_price_df):
        print('默认策略绘制基本内容')
        price_key = 'close'
        plt.title(stock_detail_map['name'] + stock_code)
        # 绘制价格线
        plt.plot(stock_price_df.index, stock_price_df[price_key], marker=',')
        plt.tight_layout()
        plt.show(block=True)
        return



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

    def print_sell_plan(self, stock_info_map):
        print('【卖出计划】code:', stock_info_map['code'], 'name:', stock_info_map['name'])
        today_close = stock_info_map['price']
        unit_ratio = 0.07
        print('买入价格：', today_close, '止损价格：', round(today_close*(1-unit_ratio), 2),
              '卖出1/3价格：', round(today_close * (1+2*unit_ratio), 2),
              '再次卖出1/3价格:', round(today_close * (1+3*unit_ratio), 2))
        print('止损时百分比：', round(unit_ratio*(-100), 2),
              '卖出1/3时百分比', round(unit_ratio * 200 * 3/2, 2),
              '再次卖出1/3时百分比', round(unit_ratio * 300 * 3, 2))
