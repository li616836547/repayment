# _*_ coding utf:8 _*_
# created 2018-4-3
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from error_method import *


def show_message(timeSeries):
    # 提供时间序列的图像、稳定性、ACF-PACF信息
    timeSeries.plot()
    test_stationarity(timeSeries)
    show_acf(timeSeries)


def show_trend(timeSeries, size):
    """
    做滚动平均的平滑处理并绘图
    :param timeSeries:时间序列
    :param size:平滑窗口大小
    :return:
    """
    f = plt.figure(facecolor='white')
    # 对size个数据进行移动平均
    rol_mean = timeSeries.rolling(window=size).mean()
    # 对size个数据进行加权移动平均
    rol_weighted_mean = pd.ewma(timeSeries, span=size)
    timeSeries.plot(color='blue', label='Original')
    rol_mean.plot(color='red', label='Rolling Mean')
    rol_weighted_mean.plot(color='black', label='Weighted Rolling Mean')
    plt.legend(loc='best')
    plt.title('Rolling Mean: window={}'.format(size))
    plt.show()


def test_stationarity(ts):
    """
    稳定性分析
    :param ts:时间序列
    :return:
    """
    dftest = adfuller(ts)
    # 对上述函数求得的值进行语义描述
    dfoutput = pd.Series(dftest[0:4],
                         index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical Value (%s)' % key] = value
    print(dfoutput)
    return dfoutput


def show_acf(timeSeries):
    """
    绘制ACF-PACF图像
    :param timeSeries: 时间序列
    """
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot(211)
    fig = sm.graphics.tsa.plot_acf(timeSeries, ax=ax1)
    ax2 = fig.add_subplot(212)
    fig = sm.graphics.tsa.plot_pacf(timeSeries, ax=ax2)


def decompose(timeSeries):
    """
    将时间序列分解为趋势、周期、残差三部分
    :param timeSeries:
    """
    decomposition = seasonal_decompose(timeSeries, model="additive")
    trend = decomposition.trend.dropna()
    seasonal = decomposition.seasonal.dropna()
    residual = decomposition.resid.dropna()
    trend.plot()
    seasonal.plot()
    residual.plot()

