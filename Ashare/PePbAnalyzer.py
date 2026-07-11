import numpy as np
import pandas as pd
import requests
import json
import argparse
import MyUtils

# 尝试导入baostock
try:
    import baostock as bs
    HAS_BAOSTOCK = True
except ImportError:
    HAS_BAOSTOCK = False
    print("baostock未安装，将使用腾讯接口估算PE/PB数据")

# 尝试导入akshare
try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False
    print("akshare未安装，将使用腾讯接口估算PE/PB数据")


def get_historical_pe_pb_baostock(stock_code, day_count=1000):
    """
    使用baostock库获取股票的历史PE和PB数据
    
    Args:
        stock_code: 股票代码（如sh000905）
        day_count: 获取的天数
    
    Returns:
        pe_pb_df: 包含PE和PB的历史数据DataFrame
    """
    try:
        print(f"正在使用baostock获取 {stock_code} 的历史PE/PB数据...")
        
        # 转换股票代码格式为baostock格式
        if stock_code.startswith('sh'):
            bs_code = 'sh.' + stock_code[2:]
        elif stock_code.startswith('sz'):
            bs_code = 'sz.' + stock_code[2:]
        else:
            bs_code = stock_code
        
        # 计算日期范围
        end_date = pd.Timestamp.now().strftime('%Y-%m-%d')
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=day_count * 2)).strftime('%Y-%m-%d')
        
        # 登录baostock
        lg = bs.login()
        
        # 获取历史估值数据
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,peTTM,pbMRQ",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="3"
        )
        
        # 转换为DataFrame
        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # 登出baostock
        bs.logout()
        
        if df is None or len(df) == 0:
            print(f"baostock未获取到数据")
            return None
        
        print(f"获取到 {len(df)} 条数据")
        
        # 选择需要的列并重命名
        pe_pb_df = df[['date', 'peTTM', 'pbMRQ']].copy()
        pe_pb_df.rename(columns={'date': 'trade_date', 'peTTM': 'pe', 'pbMRQ': 'pb'}, inplace=True)
        
        # 按日期排序
        pe_pb_df = pe_pb_df.sort_values('trade_date').reset_index(drop=True)
        
        # 处理空字符串数据
        pe_pb_df['pe'] = pd.to_numeric(pe_pb_df['pe'], errors='coerce')
        pe_pb_df['pb'] = pd.to_numeric(pe_pb_df['pb'], errors='coerce')
        
        # 过滤无效数据 - 至少PE或PB有一个有效值
        pe_pb_df = pe_pb_df[((pe_pb_df['pe'] > 0) | (pe_pb_df['pb'] > 0))]
        
        # 限制数据条数
        pe_pb_df = pe_pb_df.tail(day_count)
        
        print(f"过滤后有效数据: {len(pe_pb_df)} 条")
        
        return pe_pb_df
        
    except Exception as e:
        print(f"baostock获取数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        try:
            bs.logout()
        except:
            pass
        return None


def get_historical_pe_pb_akshare(stock_code, day_count=1000):
    """
    使用akshare库获取股票的历史PE和PB数据
    
    Args:
        stock_code: 股票代码（如sh000905）
        day_count: 获取的天数
    
    Returns:
        pe_pb_df: 包含PE和PB的历史数据DataFrame
    """
    try:
        print(f"正在使用akshare获取 {stock_code} 的历史PE/PB数据...")
        
        # 转换股票代码格式
        if stock_code.startswith('sh'):
            ts_code = stock_code[2:]
        elif stock_code.startswith('sz'):
            ts_code = stock_code[2:]
        else:
            ts_code = stock_code
        
        # 获取历史估值数据
        df = ak.stock_a_lg_indicator(symbol=ts_code)
        
        if df is None or len(df) == 0:
            print(f"akshare未获取到数据")
            return None
        
        print(f"获取到 {len(df)} 条数据")
        print(f"数据列: {df.columns.tolist()}")
        
        # 选择需要的列
        if 'pe' in df.columns and 'pb' in df.columns:
            pe_pb_df = df[['date', 'pe', 'pb']].copy()
        elif 'pe_ttm' in df.columns and 'pb' in df.columns:
            pe_pb_df = df[['date', 'pe_ttm', 'pb']].copy()
            pe_pb_df.rename(columns={'pe_ttm': 'pe'}, inplace=True)
        else:
            print(f"数据中不包含PE/PB字段，可用字段: {df.columns.tolist()}")
            return None
        
        # 重命名列
        pe_pb_df.rename(columns={'date': 'trade_date'}, inplace=True)
        
        # 按日期排序
        pe_pb_df = pe_pb_df.sort_values('trade_date').reset_index(drop=True)
        
        # 过滤无效数据
        pe_pb_df = pe_pb_df[(pe_pb_df['pe'] > 0) & (pe_pb_df['pb'] > 0)]
        
        # 限制数据条数
        pe_pb_df = pe_pb_df.tail(day_count)
        
        print(f"过滤后有效数据: {len(pe_pb_df)} 条")
        
        return pe_pb_df
        
    except Exception as e:
        print(f"akshare获取数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_historical_pe_pb_tencent(stock_code, day_count=1000):
    """
    使用腾讯接口估算股票的历史PE和PB数据（备用方案）
    
    Args:
        stock_code: 股票代码（如sh000905）
        day_count: 获取的天数
    
    Returns:
        pe_pb_df: 包含PE和PB的历史数据DataFrame
    """
    try:
        print(f"正在使用腾讯接口估算 {stock_code} 的历史PE/PB数据...")
        
        # 腾讯接口只返回当前PE/PB，不返回历史数据
        stock_map = MyUtils.get_from_gtime(stock_code)
        
        if len(stock_map) == 0:
            print(f"无法获取 {stock_code} 的当前数据")
            return None
        
        # 获取历史价格数据
        stock_price_df = MyUtils.get_price_tx(stock_code, frequency='1d', count=day_count)
        
        if stock_price_df is None or len(stock_price_df) == 0:
            print(f"无法获取 {stock_code} 的历史价格数据")
            return None
        
        # 当前PE和PB
        current_pe = stock_map.get('pe', 0)
        current_pb = stock_map.get('pb', 0)
        
        # 获取最新收盘价
        latest_close = stock_price_df['close'].iloc[-1]
        
        # 基于价格变化估算历史PE/PB
        # 假设EPS和BPS不变，PE与价格成正比，PB与价格成正比
        pe_pb_data = []
        
        for index, row in stock_price_df.iterrows():
            close_price = row['close']
            date_str = index.strftime('%Y%m%d')
            
            # 估算历史PE和PB
            estimated_pe = current_pe * (close_price / latest_close) if current_pe > 0 else 0
            estimated_pb = current_pb * (close_price / latest_close) if current_pb > 0 else 0
            
            pe_pb_data.append({
                'trade_date': date_str,
                'pe': estimated_pe,
                'pb': estimated_pb
            })
        
        pe_pb_df = pd.DataFrame(pe_pb_data)
        
        print(f"估算得到 {len(pe_pb_df)} 条历史PE/PB数据")
        
        return pe_pb_df
        
    except Exception as e:
        print(f"腾讯接口获取数据时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_historical_pe_pb(stock_code, day_count=1000):
    """
    获取股票的历史PE和PB数据（优先尝试baostock，其次akshare，失败则使用腾讯接口估算）
    
    Args:
        stock_code: 股票代码（如sh000905）
        day_count: 获取的天数
    
    Returns:
        pe_pb_df: 包含PE和PB的历史数据DataFrame
        is_estimated: 是否为估算数据
    """
    # 如果安装了baostock，优先尝试获取真实历史数据
    if HAS_BAOSTOCK:
        pe_pb_df = get_historical_pe_pb_baostock(stock_code, day_count)
        
        if pe_pb_df is not None and len(pe_pb_df) > 0:
            return pe_pb_df, False
    
    # 如果安装了akshare，尝试获取真实历史数据
    if HAS_AKSHARE:
        pe_pb_df = get_historical_pe_pb_akshare(stock_code, day_count)
        
        if pe_pb_df is not None and len(pe_pb_df) > 0:
            return pe_pb_df, False
    
    # 使用腾讯接口估算
    pe_pb_df = get_historical_pe_pb_tencent(stock_code, day_count)
    
    if pe_pb_df is not None and len(pe_pb_df) > 0:
        return pe_pb_df, True
    
    print(f"无法获取历史PE/PB数据，返回None")
    return None, False


def calculate_percentile(value, data_list):
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


def analyze_pe_pb(stock_code, day_count=1000):
    """
    分析股票的PE和PB分位情况
    
    Args:
        stock_code: 股票代码（如sh000905）
        day_count: 获取的天数
    
    Returns:
        analysis_result: 分析结果字典
    """
    # 获取当前PE和PB
    stock_map = MyUtils.get_from_gtime(stock_code)
    if len(stock_map) == 0:
        print(f"无法获取 {stock_code} 的当前数据")
        return None
    
    stock_name = stock_map.get('name', '')
    current_pe = stock_map.get('pe', 0)
    current_pb = stock_map.get('pb', 0)
    
    print(f"正在分析股票: {stock_code} ({stock_name})，历史天数: {day_count}")
    
    # 获取历史PE和PB数据
    pe_pb_df, is_estimated = get_historical_pe_pb(stock_code, day_count)
    
    if pe_pb_df is None or len(pe_pb_df) == 0:
        print(f"无法获取 {stock_code} 的历史PE/PB数据")
        return None
    
    # 计算分位
    pe_percentile = None
    pb_percentile = None
    
    # PE分位计算
    pe_data = pe_pb_df['pe'].tolist()
    pe_data = [x for x in pe_data if x > 0]
    if current_pe > 0 and len(pe_data) > 0:
        pe_percentile = calculate_percentile(current_pe, pe_data)
    
    # PB分位计算
    pb_data = pe_pb_df['pb'].tolist()
    pb_data = [x for x in pb_data if x > 0]
    if current_pb > 0 and len(pb_data) > 0:
        pb_percentile = calculate_percentile(current_pb, pb_data)
    
    # 获取统计信息
    pe_stats = None
    if len(pe_data) > 0:
        pe_stats = {
            'min': round(min(pe_data), 2),
            'max': round(max(pe_data), 2),
            'mean': round(sum(pe_data) / len(pe_data), 2),
            'median': round(sorted(pe_data)[len(pe_data) // 2], 2),
            'current': round(current_pe, 2),
            'percentile': pe_percentile
        }
    
    pb_stats = None
    if len(pb_data) > 0:
        pb_stats = {
            'min': round(min(pb_data), 2),
            'max': round(max(pb_data), 2),
            'mean': round(sum(pb_data) / len(pb_data), 2),
            'median': round(sorted(pb_data)[len(pb_data) // 2], 2),
            'current': round(current_pb, 2),
            'percentile': pb_percentile
        }
    
    analysis_result = {
        'stock_code': stock_code,
        'stock_name': stock_map.get('name', ''),
        'pe_stats': pe_stats,
        'pb_stats': pb_stats,
        'data_points': len(pe_pb_df),
        'is_estimated': is_estimated
    }
    
    return analysis_result


def print_analysis_result(result):
    """
    打印分析结果
    
    Args:
        result: 分析结果字典
    """
    if result is None:
        return
    
    print(f"\n{'='*60}")
    print(f"股票代码: {result['stock_code']}")
    print(f"股票名称: {result['stock_name']}")
    print(f"数据点数: {result['data_points']}")
    if result.get('is_estimated', False):
        print(f"数据来源: 基于价格估算（真实历史PE/PB数据不可用）")
        print(f"注意: 估算数据假设EPS和BPS不变，仅供参考")
    else:
        print(f"数据来源: 真实历史PE/PB数据")
    print(f"{'='*60}")
    
    # PE分析
    print("\n【PE市盈率分析】")
    pe = result['pe_stats']
    if pe is not None:
        print(f"当前PE: {pe['current']}")
        print(f"历史最低PE: {pe['min']}")
        print(f"历史最高PE: {pe['max']}")
        print(f"历史平均PE: {pe['mean']}")
        print(f"历史中位PE: {pe['median']}")
        print(f"当前PE分位: {pe['percentile']}%")
        
        if pe['percentile'] is not None:
            if pe['percentile'] < 20:
                print("评价: 当前PE处于历史低位，可能被低估")
            elif pe['percentile'] < 50:
                print("评价: 当前PE处于历史中位偏低")
            elif pe['percentile'] < 80:
                print("评价: 当前PE处于历史中位偏高")
            else:
                print("评价: 当前PE处于历史高位，可能被高估")
    else:
        print("数据不足，无法计算PE分位")
    
    # PB分析
    print("\n【PB市净率分析】")
    pb = result['pb_stats']
    if pb is not None:
        print(f"当前PB: {pb['current']}")
        print(f"历史最低PB: {pb['min']}")
        print(f"历史最高PB: {pb['max']}")
        print(f"历史平均PB: {pb['mean']}")
        print(f"历史中位PB: {pb['median']}")
        print(f"当前PB分位: {pb['percentile']}%")
        
        if pb['percentile'] is not None:
            if pb['percentile'] < 20:
                print("评价: 当前PB处于历史低位，可能被低估")
            elif pb['percentile'] < 50:
                print("评价: 当前PB处于历史中位偏低")
            elif pb['percentile'] < 80:
                print("评价: 当前PB处于历史中位偏高")
            else:
                print("评价: 当前PB处于历史高位，可能被高估")
    else:
        print("数据不足，无法计算PB分位")
    
    print(f"\n{'='*60}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取股票PE/PB历史数据并分析分位情况')
    parser.add_argument('stock_code', type=str, nargs='?', default='sz000001', help='股票代码（如sh000905）')
    parser.add_argument('day_count', type=int, nargs='?', default=1000, help='历史天数')
    args = parser.parse_args()
    
    stock_code = args.stock_code
    day_count = args.day_count
    
    # 分析PE和PB分位情况
    result = analyze_pe_pb(stock_code, day_count)
    
    # 打印分析结果
    print_analysis_result(result)
