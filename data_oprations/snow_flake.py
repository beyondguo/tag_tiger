# -*- encoding:utf-8 -*-

import time

class MySnow:
    def __init__(self, dataID):
        self.start = int(time.mktime(time.strptime('2018-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")))
        self.last = int(time.time())
        self.countID = 0
        self.dataID = dataID  # 数据ID，这个自定义或是映射

    def get_id(self):
        # 时间差部分
        now = int(time.time())
        temp = now - self.start
        if len(str(temp)) < 9:  # 时间差不够9位的在前面补0
            length = len(str(temp))
            s = "0" * (9 - length)
            temp = s + str(temp)
        if now == self.last:
            self.countID += 1  # 同一时间差，序列号自增
        else:
            self.countID = 0  # 不同时间差，序列号重新置为0
            self.last = now
        # 标识ID部分
        if len(str(self.dataID)) < 2:
            length = len(str(self.dataID))
            s = "0" * (2 - length)
            self.dataID = s + str(self.dataID)
        # 自增序列号部分
        if self.countID == 99999:  # 序列号自增5位满了，睡眠一秒钟
            time.sleep(1)
        countIDdata = str(self.countID)
        if len(countIDdata) < 5:  # 序列号不够5位的在前面补0
            length = len(countIDdata)
            s = "0" * (5 - length)
            countIDdata = s + countIDdata
        id = str(temp) + str(self.dataID) + countIDdata
        return id

