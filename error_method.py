# _*_ coding utf-8 _*_
# by Li Hanpeng
# 用于计算各种误差
import numpy as np
import pandas as pd


# print各种误差值
def show_errors(real, predicted):
    print('------------------------------------')
    print('误差分析：')
    print('MSE is {:.4f}'.format(mse(real, predicted)))
    print('RMSE is {:.4f}'.format(rmse(real, predicted)))
    print('MAE is {:.4f}'.format(mae(real, predicted)))
    # print('R2 is {:.4f}'.format(r2(real, predicted)))
    print('MAPE is {:.4f}%'.format(mape(real, predicted)))


# 预处理，将输入参数转为Series类型，并计算a,b的差
def deviation(a, b):
    a = pd.Series(a).dropna()
    b = pd.Series(b).dropna()
    d = (a - b).dropna()
    return a, b, d


# 均方误差 mean-square-error
def mse(a, b):
    a, b, d = deviation(a, b)
    return sum(d**2)/d.size


# 均方根误差 root-mean-square-error
def rmse(a, b):
    return np.sqrt(mse(a, b))


# 平均绝对误差 mean-absolute-error
def mae(a, b):
    a, b, d = deviation(a, b)
    return sum(np.abs(d))/d.size


# 平均绝对百分误差 mean-absolute-percent-error
def mape(real, predicted):
    real, predicted, d = deviation(real, predicted)
    return sum((np.abs(d/real)).dropna())*100/d.size


# 拟合优度
def r2(real, predicted):
    real, predicted, d = deviation(real, predicted)
    ssreg = np.sum((predicted - real.mean()) ** 2)
    sstot = np.sum((real - real.mean()) ** 2)
    return ssreg/sstot



