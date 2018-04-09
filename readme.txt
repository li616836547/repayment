2018-4-3

1、运行方法
    执行main.py文件
2、软件环境
    python 3.6
    numpy 1.14.0
    pandas 0.22.0
    matplotlib 2.1.2
    statsmodels 0.8.0
2、模块介绍
    main.py：主文件,包括数据的读取、建模分析和数据导出等功能
    error_method: 提供了几个常见的误差分析的函数，如MSE等
    analysis_method: 该模块提供了可能用到的几种分析函数，包括稳定性、自相关性等。
    holiday_effect: 提供了HolidayEffect类，用于对数据的特殊日期进行加权处理以及加权后数据的还原。
    data.sql: 原始数据，因txt、csv等格式易被加密，所以保存格式为*.sql
    html文件夹： 储存生成的图片文件和html文件。
