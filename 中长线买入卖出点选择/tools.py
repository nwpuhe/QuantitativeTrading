from gm.api import *
from MSCI_tools import msci_tools
import numpy as np
from MSCI_tools import 计算贝塔值和自定义的波动率_ as beta_and_vol


def buy_check(context,symbol):
    return buy_check_volume_increase_and_price_amplitude(context, symbol)



#定义60天的波动率小于10%，完成以后可以改成
def buy_check_price_amplitude(context, symbol, count = 60, threshold = 0.1):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)

    #amplitude = beta_and_vol.get_volatility_normal(symbol,last_day,count=count)

    data = history_n(symbol,frequency="1d",count=count,end_time=last_day,fields="open,high,low,close")
    close = msci_tools.get_data_value(data,"close")
    open = msci_tools.get_data_value(data, "open")
    high = msci_tools.get_data_value(data, "high")
    low = msci_tools.get_data_value(data, "low")

    amplitude = (np.max(high) - np.min(low))/close[0]

    if amplitude < threshold:
        return True
    else:
        return False

# 买入点-地量（连续18周成交量小于最近4年内天量的10%）
def buy_check_mean_volume_small(context, symbol,week_count_short=18 ,week_count_long = 150, threshold = 0.1):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)

    data = history_n(symbol, frequency="1d", count=week_count_long * 5, end_time=last_day, fields="volume")
    volume = msci_tools.get_data_value(data,"volume")
    max_volume_last = np.max(volume[-week_count_short*5:])
    max_volume = np.max(volume)

    if max_volume_last < max_volume * 0.1:
        return True
    else:
        return False


# 单日成交量大于该股的前五日移动平均成交量2.5倍，大于前10日移动平均成交量3倍
def buy_check_volume_increase(context, symbol):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)

    data = history_n(symbol, frequency="1d", count=11, end_time=last_day, fields="volume")
    volume = msci_tools.get_data_value(data,"volume")
    h = volume
    volume = h['volume'][-1]
    volume_mean_5 = np.mean(h['volume'][-6:-1])
    volume_mean_10 = np.mean(h['volume'][-11:-1])
    if volume > volume_mean_5 * 2.5 and volume > volume_mean_10 * 3:
        return True
    else:
        return False



# 找到昨天之前成交量大于昨天的成交量（0.8倍），这个区间的天数大于30天
# 昨天单日成交量大于该区间的平均成交量的2倍
# 区间价格波动小于10%
def buy_check_volume_increase_and_price_amplitude(context, symbol):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)

    data = history_n(symbol, frequency="1d", count=270, end_time=last_day, fields="open,high,low,close,volume")

    close = msci_tools.get_data_value(data,"close")
    open = msci_tools.get_data_value(data, "open")
    high = msci_tools.get_data_value(data, "high")
    low = msci_tools.get_data_value(data, "low")
    volume = msci_tools.get_data_value(data,"volume")

    volume_yesterday = volume[-1]

    try:
        # 昨日收盘价要高于开盘价
        if close[-1] < open[-1]:
            return False
    except:return False

    # 找到昨天之前成交量大于昨天的成交量（0.8倍）的那个日期，这个日期到今天的区间的天数大于30天
    start = 0
    end = -1
    for i in range(1, len(volume)):
        index = -(i + 1)
        if volume[index] > volume[-1] * 0.8:
            start = index + 1
            break
    if start == 0 or (end - start) < 30:
        return False


    # 昨天单日成交量大于该区间的平均成交量的2倍
    volume_mean = np.mean(volume[start:end])
    volume_mean_5 = np.mean(volume[-6:-1])
    if volume_yesterday < volume_mean * 2.5 or volume_yesterday < volume_mean_5 * 2.5:
       return False

    # 区间价格波动小于10%
    price_max = max(high[start:end])
    price_min = min(low[start:end])
    price_amplitude = (price_max - price_min) / open[start]
    # print 'min=%s, max=%s, open=%s, amplitude=%s' % (price_min, price_max, h['open'][start], price_amplitude)
    if price_amplitude > 0.1:
        return False

    return True

"""-----------------下面是卖出函数---------------------"""

#卖出点判定
def sell_check(context, symbol):
    if sell_check_mean_price(context, symbol, 0.1) and sell_check_turnover_ratio(context, symbol):
        return True
    if sell_check_mean_price(context, symbol, 0.2):
        return True
    return False


# 卖出点-均线（5日线超过10日线10%，10日线超过30日线10%）
def sell_check_mean_price(context, symbol, threshold = 0.1):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)

    data = history_n(symbol, frequency="1d", count=31, end_time=last_day, fields="open,high,low,close,volume")

    close = msci_tools.get_data_value(data, "close")
    open = msci_tools.get_data_value(data, "open")
    high = msci_tools.get_data_value(data, "high")
    low = msci_tools.get_data_value(data, "low")
    volume = msci_tools.get_data_value(data, "volume")

    # 求5日线、10日线、30日线
    mean_5 = np.mean(close[-5:])
    mean_10 = np.mean(close[-10:])
    mean_30 = np.mean(close[-30:])
    diff_5_10 = (mean_5 - mean_10) / mean_10
    diff_5_30 = (mean_5 - mean_30) / mean_30
    diff_10_30 = (mean_10 - mean_30) / mean_30

    # 求昨天的求5日线、10日线、30日线
    yes_mean_5 = np.mean(close[-6:-1])
    yes_mean_10 = np.mean(close[-11:-1])
    yes_mean_30 = np.mean(close[-31:-1])
    yes_diff_5_10 = (yes_mean_5 - yes_mean_10) / yes_mean_10
    yes_diff_5_30 = (yes_mean_5 - yes_mean_30) / yes_mean_30
    yes_diff_10_30 = (yes_mean_10 - yes_mean_30) / yes_mean_30

    return diff_5_30 > threshold


#卖出点-换手率
def sell_check_turnover_ratio(context, symbol):

    now = context.now
    last_day = get_previous_trading_date("SHSE", now)
    #换手率
    _df = get_fundamentals(table='trading_derivative_indicator', symbols=symbol, start_date=last_day,
                           end_date=last_day, fields='TURNRATE')

    TURNRATE = msci_tools.get_data_value(_df,"TURNRATE")
    return TURNRATE[0]>15

#卖出点RSRS
from MSCI_tools import 计算RSRS as RSRS
def sell_check_rsrs(context,symbol):
    threshold = -0.7
    now = context.now
    zscore_rightdev = RSRS.get_rsrs_weight_classic(symbol,now)

    if zscore_rightdev < threshold:
        return True
    else:
        return False



# 庄股值计算   庄股：能够无量涨停的或无量杀跌的。 庄股值：成为庄股的可能性
def cow_stock_value(context, symbol):
    now = context.now
    _pb = get_fundamentals(table='trading_derivative_indicator', symbols=symbol, start_date=now,
                           end_date=now, fields='PB,NEGOTIABLEMV')
    pb = msci_tools.get_data_value(_pb, "PB")
    NEGOTIABLEMV = (msci_tools.get_data_value(_pb, "NEGOTIABLEMV"))[0]/100000000

    if NEGOTIABLEMV > 100:
        return 0
    num_fall = fall_money_day_3line(context, symbol, 120, 20, 60, 160)
    num_cross = money_5_cross_60(context, symbol, 120, 5, 160)
    return (num_fall * num_cross) / (pb *(NEGOTIABLEMV ** 0.5))



# 3条移动平均线计算缩量
def fall_money_day_3line(context,symbol,n,n1=20,n2=60,n3=120):
    now = context.now
    last_day = get_previous_trading_date("SHSE",now)

    data = history_n(symbol, frequency="1d", count=n+n3, end_time=last_day, fields="cum_volume")
    stock_m = msci_tools.get_data_value(data,"cum_volume")
    i=0
    count=0
    while i<n:
        money_MA200=np.mean(stock_m[i:n3-1+i])
        money_MA60=np.mean(stock_m[i+n3-n2:n3-1+i])
        money_MA20=np.mean(stock_m[i+n3-n1:n3-1+i])
        if money_MA20<=money_MA60 and money_MA60<=money_MA200:
            count=count+1
        i=i+1
    return count


# 计算脉冲（1.0版本） 成交额5日穿60日？
def money_5_cross_60(context, symbol, n, n1 = 5, n2 = 60):
    now = context.now
    last_day = get_previous_trading_date("SHSE",now)

    data = history_n(symbol, frequency="1d", count=n+n2+1, end_time=last_day, fields="cum_volume")
    stock_m = msci_tools.get_data_value(data,"cum_volume")
    i=0
    count=0
    while i<n:
        money_MA60=np.mean(stock_m[i+1:n2+i])
        money_MA60_before=np.mean(stock_m[i:n2-1+i])
        money_MA5=np.mean(stock_m[i+1+n2-n1:n2+i])
        money_MA5_before=np.mean(stock_m[i+n2-n1:n2-1+i])
        if (money_MA60_before-money_MA5_before)*(money_MA60-money_MA5)<0:
            count=count+1
        i=i+1
    return count



if __name__ == "__main__":

    res_1 =  get_fundamentals(table='trading_derivative_indicator', symbols="SZSE.300296", start_date="2018-06-25",
                           end_date="2018-06-25", fields='PB,NEGOTIABLEMV')
    pb = msci_tools.get_data_value(res_1,"PB")
    NEGOTIABLEMV = msci_tools.get_data_value(res_1,"NEGOTIABLEMV")
    print(NEGOTIABLEMV[0]/100000000)