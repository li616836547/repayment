# _*_ coding utf:8 _*_
# Li Hanpeng 2018-3-9
import pandas as pd
from datetime import datetime
from datetime import timedelta
import calendar


class HolidayEffect(object):
    """
    对数据进行节假日加权处理的类，主要包括节假日日期的配置，样本中对节假日加权处理，以及恢复加权后的时间序列等方法。
    属性介绍：
        节假日和统一还款日，格式为字典类型{放假开始日期：放假持续时长}。在__init__构造函数中会自动转为[start_date~end_date]的列表
        united_repayment_day:统一还款日,即23号
        spring_festival:春节长假起始日期及持续天数
        holiday:普通假日的起始日期及持续天数，如清明节、元旦等
        权重属性，float类型，存储各种权重值
        spring_festival_weight: 春节期间权重
        holiday_weight： 普通假日期间权重
        before_holiday_weight: 还款序列的特点是节前，节后还款额较高，过节期间还款额比平常低，因此考虑了节前权重
        after_holiday_weight: 节后权重，意义同上
        united_repayment_weight: 统一还款日权重
        month_end_weight: 月末（每月28号及以后）到期还款的人还款日统一为同意还款日，因此其权重也有变化
    """
    united_repayment_day = 23
    spring_festival = {'2018-2-15': 7}
    holiday = {'2017-12-30': 3, '2018-4-5': 3}
    # 调整权重，其中同意还款日和月末为加权重，其余为乘权重
    spring_festival_weight = 1
    holiday_weight = 1
    before_holiday_weight = 1
    after_holiday_weight = 1
    united_repayment_weight = 0.055
    month_end_weight = 0.093

    def __init__(self):
        """
        初始化HolidayEffect类，将配置的字典格式的节日日期转为日期列表，使其易于后续处理。
        并生成节前日期表（节前一天）和节后日期表（节后一天），便于后续对节前节后还款额针对性加权处理。
        如{'2018-1-1':3}转为['2018-1-1','2018-1-2','2018-1-3']
        """
        before_holiday = []
        after_holiday = []
        holiday = []
        for start, periods in self.spring_festival.items():
            spring_festival = list(pd.date_range(start, periods=periods))
            before_holiday.append(spring_festival[0] - timedelta(1))
            after_holiday.append(spring_festival[-1] + timedelta(1))
            self.spring_festival = spring_festival
        for start, periods in self.holiday.items():
            holiday.extend(list(pd.date_range(start, periods=periods)))
            before_holiday.append(datetime.strptime(start, '%Y-%m-%d') - timedelta(1))
            after_holiday.append(datetime.strptime(start, '%Y-%m-%d') + timedelta(periods))
            self.holiday = holiday

    def weighting(self, timeseries):
        """
        找出时间序列中的特殊日期，如节日，统一还款日等，并为特殊日期加权处理。
        :param timeseries: 待处理的时间序列
        :return: 加权后的时间序列
        """
        for date in timeseries.index:
            if date in self.spring_festival:
                timeseries[date] = timeseries[date] * self.spring_festival_weight
            elif date in self.holiday:
                timeseries[date] = timeseries[date] * self.holiday_weight
            if date.day == self.united_repayment_day:
                if date.month < 12:
                    # ratio表示该月有几天的还款日被分配到同意还款日中，如一月有28，29，30，31，ratio=4，17年2月有28，ratio=1
                    ratio = calendar.monthrange(date.year, date.month)[1] - 27
                    timeseries[date] = timeseries[date] * (1 - ratio * self.united_repayment_weight)
            elif date.day in [28, 29, 30, 31]:
                if date.month < 12:
                    timeseries[date] = timeseries[date] * (1 + self.month_end_weight)
        return timeseries

    def recover(self, timeseries):
        """
        weighting函数的逆过程，去掉特殊日期加的权重，使其恢复至原始状态
        :param timeseries: 待处理的时间序列
        :return: 恢复后的时间序列
        """
        for date in timeseries.index:
            if date in self.spring_festival:
                timeseries[date] * 1/self.spring_festival_weight
            elif date in self.holiday:
                timeseries[date] * 1/self.holiday_weight
            if date.day == self.united_repayment_day:
                if date.month<12:
                    ratio = calendar.monthrange(date.year, date.month)[1] - 27
                    timeseries[date] = timeseries[date] / (1 - ratio*self.united_repayment_weight)
            elif date.day in [28, 29, 30, 31]:
                if date.month<12:
                    timeseries[date] = timeseries[date] / (1 + self.month_end_weight)
        return timeseries