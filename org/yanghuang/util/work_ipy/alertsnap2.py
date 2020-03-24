# coding=UTF-8

import json
import re
from os.path import expanduser
import os
import io
from typing import TextIO

# 判断日期时间开头字串的正则表达式
dateTimePattern = re.compile('\[\d\d\d\d-\d\d-\d\d')
# 日志行的字段分割字串
fieldSeparator = ']['
# alert信息的json key常量
alertJsonKeyTs = 'ts'
alertJsonKeyMsg = 'message'
# alert信息关键字
alertLevelFatal='FATAL'
alertLevelError='ERROR'
alertLevelWarn='WARN'
alertLevelINFO='INFO'
alertKeywordsException='exception'
alertKeywordsFatalError='fatal error'

def isTimeLine(line_splits):
    if line_splits == None or len(line_splits) == 0:
        return False
    if dateTimePattern.match(line_splits[0]):
        return True
    else:
        return False


def isLogLevelLine(line_splits, level):
    if line_splits == None or len(line_splits) < 2:
        return False
    if level == line_splits[1].upper():
        return True
    else:
        return False


def isErrorLine(line_splits):
    return isLogLevelLine(line_splits, alertLevelError)


def isWarnLine(line_splits):
    return isLogLevelLine(line_splits, alertLevelWarn)


def isInfoLine(line_splits):
    return isLogLevelLine(line_splits, alertLevelINFO)


def isExceptionLine(line_splits):
    if line_splits == None or len(line_splits) < 3:
        return False
    for i in range(2, len(line_splits)):
        if alertKeywordsException in line_splits[i].lower():
            return True
    return False


def isFatalLine(line_splits):
    # slf4j没有fatal级别，但也检查
    isFatal = isLogLevelLine(line_splits, alertLevelFatal)
    if isFatal:
        return True
    if line_splits == None or len(line_splits) < 3:
        return False
    for i in range(2, len(line_splits)):
        if alertKeywordsFatalError in line_splits[i].lower():
            return True
    return False


def findFileAlerts(alerts,log_file,prev_time_field,after_lines):
    msg_line_count = 0
    for line in log_file:
        line_splits = line.split(fieldSeparator)
        if msg_line_count > 0 and msg_line_count < after_lines+1:
            if not isTimeLine(line_splits):
                msg_line_count += 1
                alerts[len(alerts) - 1][alertJsonKeyMsg] += line
            else:
                msg_line_count = 0
        if not isTimeLine(line_splits):
            continue
        time_field = line_splits[0]
        if time_field <= prev_time_field:
            continue
        if isFatalLine(line_splits) or isErrorLine(line_splits) or isExceptionLine(line_splits):
            msg_line_count = 1
            alert_msg = dict()
            alert_msg[alertJsonKeyTs] = time_field
            alert_msg[alertJsonKeyMsg] = line
            alerts.append(alert_msg)

def findAlerts(file_path, prev_time_field, after_lines=2):
    '''
    在传入的文件中查询报错日志信息，组织为json列表。
    :param file_path: 日志文件路径
    :param prev_time_field: 上次已经报警的最后时间字串，格式为'[2020-03-24 20:21:22.023'
    :param after_lines: 报警行，再取后续行数
    :return: 报警信息列表，列表元素为：['ts']=报警时间，格式为'[2020-03-24 20:21:22.023';['message']=详细信息
    '''
    alerts = list()
    with io.open(file_path,encoding='utf-8') as log_file:
        prev_time_str=''
        if prev_time_field!=None:
            prev_time_str=prev_time_field
        findFileAlerts(alerts,log_file,prev_time_str,after_lines)
    return alerts

def buildFileFullPath(log_file_path):
    home=expanduser('~')
    return home+'/'+'.alert_log.' + log_file_path.replace('/', '-').replace('\\', '_').replace(':','.')

def savePreAlerts(file_path, alerts):
    alert_file_path = buildFileFullPath(file_path)
    with io.open(alert_file_path,'w',encoding='utf-8') as storedFile:
        try:
            storedFile.write(json.dumps(alerts).encode('utf-8'))
            #json.dump(alerts, storedFile)
        except Exception as e:
            print(e)

def readFromFile(file_path):
    alert_file_path = buildFileFullPath(file_path)
    if os.path.exists(alert_file_path):
        with io.open(alert_file_path,'r',encoding='utf-8') as storedFile:
            try:
                return json.load(storedFile)
            except Exception as e:
                print(e)
    return dict()

if __name__ == '__main__':
    
    line = '[2020-03-24][ERROR][ID]: fatal error, NullPointException'
    print(isExceptionLine(line.split('][')))
    file_path='/data/temp/alert_log.txt'
    alerts=findAlerts(file_path,'',3)
    savePreAlerts(file_path,alerts)
    print(alerts)




