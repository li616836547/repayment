# _*_ coding utf:8 _*_
# created 2018-4-3

import copy
import logging
from scipy.optimize import leastsq
from datetime import datetime, timedelta
from statsmodels.tsa.arima_model import ARMA
from holiday_effect import HolidayEffect
from analysis_method import *
from error_method import *
import matplotlib.pyplot as plt
import os


def read_data(data, sample_start, sample_end, data_start=datetime(2017, 11, 30), skiprows=1):
    """
    读取没有时间索引的data，将其转为Series类型的原始数据和样本
    :param data: ndarray类型，无时间索引的原始数据
    :param data_start: 原始数据的开始日期
    :param sample_start: 样本数据的开始日期
    :param sample_end: 样本数据的结束日期
    :return: data:原始数据，即所有数据
             sample: 建模时实际采用的数据
    """
    data_end = data_start + timedelta(data.size-1)
    data = pd.Series(data, index=pd.date_range(data_start, periods=data.size))
    sample = copy.deepcopy(data[sample_start: sample_end])
    logging.info('正在读取数据...')
    logging.info('原始数据：{} ~ {}，共计{}天'.format(data_start, data_end, data.size))
    logging.info('样本数据：{} ~ {}，共计{}天'.format(sample_start, sample_end, sample.size))
    return data, sample


def automatic_analysis(data, data_start=datetime(2017, 11, 30)):
    """
    自动化预测时调用的方法，配置样本时间和预测时间，默认预测下一个七天的还款额
    :param data: Dataframe类型，原始数据
    :param data_start: 原始数据的开始日期
    :return: 样本的起止日期，预测的起止日期
    """
    data_end = data_start + timedelta(data.size-1)
    sample_start = data_start
    sample_end = data_end
    predict_days = 7
    predict_start = sample_end + timedelta(1)
    predict_end = sample_end + timedelta(predict_days)
    return sample_start, sample_end, predict_start, predict_end, predict_days


def to_html(result, fig_path):
    """
    将预测结果转化为html
    :param result: str,文字版预测结果
    :param fig_path: str,预测结果图片的路径
    :return: str类型, html文件的字节码
    """
    html_result = pd.DataFrame(result).to_html(header=False, index=True)
    html_result = html_result.replace('<table border="1" class="dataframe">', '<table border="1" class="dataframe"， align="center">')
    html = """
    <html>
        <head>
            <meta http-equiv="content-type" content="text/html;charset=utf-8">
            <title>还款分析</title>
        </head>
        <body>
            <h1 align="center">{}日还款分析</h1>
            {}
            <img src="{}" style="margin: 0 auto;"> 
        </body>
    </html>""".format(datetime.now().date(), html_result, fig_path)
    return html


if __name__ == '__main__':

    # 样本集和预测集配置
    is_automatic = False
    data_start = '2017-11-30'
    sample_start = '2017-11-30'
    sample_end = '2018-3-31'
    predict_days = 7
    predict_start = None
    # 数据处理配置
    drop = False
    holiday = True
    smooth = False
    log = True
    diff1 = True
    diff7 = True
    # ARMA模型配置
    p = 2
    q = 1
    # 输出配置
    logging_level = logging.INFO
    fig_folder = 'fig'
    html_folder = 'html'

    # 初始化
    logging.basicConfig(level=logging_level)
    data_start = datetime.strptime(data_start, '%Y-%m-%d').date()
    sample_start = datetime.strptime(sample_start, '%Y-%m-%d').date()
    sample_end = datetime.strptime(sample_end, '%Y-%m-%d').date()
    data = np.loadtxt('data.sql', dtype='float', delimiter=',', skiprows=1, encoding='utf-8')
    data_end = data_end = data_start + timedelta(data.size-1)
    if not predict_start:
        predict_start = sample_end + timedelta(1)
    if predict_days < 0 or not isinstance(predict_days, int):
        raise ValueError('预测天数应该为正整数')
    predict_end = predict_start + timedelta(predict_days-1)
    predict_index = pd.date_range(predict_start, predict_end)
    if sample_end > data_end:
        raise ValueError('样本结束日期{}大于原始数据最后一条日期{}!'.format(sample_end, data_end))
    if is_automatic:
        sample_start, sample_end, predict_start, predict_end, predict_days = automatic_analysis(data, data_start)
    data, sample = read_data(data, sample_start, sample_end, data_start)
    logging.info('预测时间段：{} ~ {}，共计{}天'.format(predict_start, predict_end, predict_days))

    # 数据处理
    process_list = [sample]
    task_list = ['drop', 'holiday', 'smooth', 'log', 'diff1', 'diff7']
    for task in task_list:
        if not eval(task):
            task_list.remove(task)
    logging.info('正在进行数据处理...')
    logging.info('处理方法依次为' + str(task_list))
    if drop:
        processing = process_list[-1]
        drop_sample = pd.concat([sample[:'2018-2-13'], sample['2018-2-23':]])
        process_list.append(drop_sample)
    if holiday:
        processing = process_list[-1]
        he = HolidayEffect()
        holiday_sample = he.weighting(processing)
        process_list.append(holiday_sample)
    if smooth:
        processing = process_list[-1]
        smooth_sample = processing.rolling(window=7).mean().dropna()
        process_list.append(smooth_sample)
    if log:
        processing = process_list[-1]
        log_sample = np.log(processing)
        process_list.append(log_sample)
    if diff1:
        processing = process_list[-1]
        diff1_sample = processing.diff(1).dropna()
        process_list.append(diff1_sample)
    if diff7:
        processing = process_list[-1]
        diff7_sample = processing.diff(7).dropna()
        process_list.append(diff7_sample)

    # ARMA建模
    logging.info('正在建模分析...')
    processing = process_list.pop()
    processing.index = pd.date_range(processing.index[0], periods=processing.size)
    predict_false_start = processing.index[-1] + timedelta(1)
    predict_false_end = processing.index[-1] + timedelta(predict_days)
    model = ARMA(processing, order=(p, q)).fit(disp=-1, method='css')
    logging.info('模型的aic,bic,hqic值分别为：{},{},{}'.format(model.aic, model.bic, model.hqic))
    predict_ts = model.predict(start=predict_false_start, end=predict_false_end)
    recover = predict_ts

    # 复原
    if diff7:
        processing = process_list.pop()
        diff_recover_1 = pd.Series([0.0]*recover.size, index=recover.index)
        for i in recover.index:
            if i-timedelta(7) in processing.index:
                diff_recover_1[i] = recover[i] + processing[i-timedelta(7)]
            else:
                diff_recover_1[i] = recover[i] + diff_recover_1[i - timedelta(7)]
        recover = diff_recover_1
    if diff1:
        processing = process_list.pop()
        diff_recover = recover.cumsum() + processing[-1]
        recover = diff_recover
    if log:
        processing = process_list.pop()
        log_recover = np.exp(recover)
        recover = log_recover
    if smooth:
        processing = process_list.pop()
        processing = processing[-6:]
        rol_recover = pd.Series([0.0]*predict_days, index=pd.date_range(predict_false_start, predict_false_end))
        for i in range(predict_days):
            rol_sum = processing.rolling(window=6).sum()[-1]
            date_index = predict_false_start + timedelta(i)
            rol_recover[date_index] = recover[date_index] * 7 - rol_sum
            processing[date_index] = rol_recover[date_index]
        recover = rol_recover
    if holiday:
        recover.index = predict_index
        weight_recover = he.recover(recover)
        recover = weight_recover

    # 计算模型误差并绘图
    result = recover
    result.name = '还款金额'
    target_data = data[:result.index[-1]]
    if result.index[0] <= target_data.index[-1]:
        show_errors(target_data, recover)
    plt.figure(facecolor='white')
    if result.index[0] <= target_data.index[-1]:
        plt.title('还款预测MAPE: {:.4}'.format(mape(target_data, result)), fontproperties='SimHei', fontsize=15)
    plt.ylabel('还款金额（万元）', fontproperties='SimHei')
    target_data.plot(color='red', label='Original', style='.-')
    recover.plot(color='blue', label='Predict', style='.-')
    plt.legend(loc='best')
    plt.show()

    # 保存结果到图片和HTML文件
    fig_name = 'fig' + datetime.strftime(datetime.now(), format='%Y-%m-%d-%H_%M_%S' + '.png')
    fig_path = os.path.join(html_folder, fig_folder, fig_name)
    fig_relative_path = os.path.join(fig_folder, fig_name)
    if os.path.exists(fig_path):
        logging.warning('文件{}已存在！将删除原文件'.format(fig_path))
        os.remove(fig_path)
    plt.savefig(fig_path)
    html = to_html(result, fig_relative_path)
    html_name = 'html' + datetime.strftime(datetime.now(), format='%Y-%m-%d-%H_%M_%S' + '.html')
    html_path = os.path.join(html_folder, html_name)
    if os.path.exists(html_path):
        logging.warning('文件{}已存在！将删除原文件'.format(html_path))
        os.remove(html_path)
    with open(html_path, mode='w+', encoding='utf-8') as f:
        f.write(html)



