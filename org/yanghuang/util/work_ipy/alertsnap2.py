# coding=UTF-8
'''
- extract alert lines from log file
- use findAlerts(file_path, prev_time_field, after_lines=2) to snap alerts in logfile
- use saveAlerts(log_file_path, alerts) to save alerts to tmp hidden file
- use readPreSavedAlerts(log_file_path) to read last saved alerts from tmp hidden file
'''
import json
import os
import re
import sys
from os.path import expanduser
import tailer

# 最大内存持有报警条数，避免内存占用过多
maxAlertsInMem = 1000
# 最多查找日志文件尾部行数，避免过大文件，扫描时间过长
maxTailLineNum = 500000
# 判断日期时间开头字串的正则表达式
dateTimePattern = re.compile('\[\d\d\d\d-\d\d-\d\d')
# 日志行的字段分割字串
fieldSeparator = ']['
# alert信息的json key常量
alertJsonKeyTs = 'ts'
alertJsonKeyMsg = 'message'
# alert信息关键字
alertLevelFatal = 'FATAL'
alertLevelError = 'ERROR'
alertLevelWarn = 'WARN'
alertLevelINFO = 'INFO'
alertKeywordsException = 'exception'
alertKeywordsFatalError = 'fatal error'


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


def containKeywords(line_splits, keywords):
    if line_splits == None or len(line_splits) < 4:
        return False
    for i in range(3, len(line_splits)):
        try:
            start_index = line_splits[i].index(']')
            if keywords in line_splits[i][start_index:].lower():
                return True
        except:
            pass
    return False


def isExceptionLine(line_splits):
    return containKeywords(line_splits, alertKeywordsException)


def isFatalLine(line_splits):
    # slf4j没有fatal级别，但也检查
    isFatal = isLogLevelLine(line_splits, alertLevelFatal)
    if isFatal:
        return True
    return containKeywords(line_splits, alertKeywordsFatalError)


def findFileAlerts(alerts, log_file, prev_time_field, after_lines):
    if prev_time_field == None:
        prev_time_field = ''
    lines = tailer.tail(log_file, maxTailLineNum)
    msg_line_count = 0
    latest_time_field = ''
    for line in lines:
        line_splits = line.split(fieldSeparator)
        if msg_line_count > 0 and msg_line_count < after_lines + 1:
            if not isTimeLine(line_splits):
                msg_line_count += 1
                alerts[len(alerts) - 1][alertJsonKeyMsg] += ('\n' + line)
            else:
                msg_line_count = 0
        if not isTimeLine(line_splits):
            continue
        time_field = line_splits[0]
        latest_time_field = time_field
        if time_field <= prev_time_field:
            continue
        if isFatalLine(line_splits) or isErrorLine(line_splits):
            msg_line_count = 1
            alert_msg = dict()
            alert_msg[alertJsonKeyTs] = time_field
            alert_msg[alertJsonKeyMsg] = line
            alerts.append(alert_msg)
            if len(alerts) > maxAlertsInMem:
                alerts.pop(0)
    alerts.append({'ts': latest_time_field})


def findAlerts(file_path, prev_time_field, after_lines=2):
    '''
    在传入的文件中查询报错日志信息，组织为json列表。
    :param file_path: 日志文件路径
    :param prev_time_field: 上次已经报警的最后时间字串，格式为'[2020-03-24 20:21:22.023'
    :param after_lines: 报警行，再取后续行数
    :return: 报警信息列表，列表元素为：['ts']=报警时间，格式为'[2020-03-24 20:21:22.023';['message']=详细信息。
    最后一条数据不带message信息，只带ts，用于标识日志文件扫描到的时间点，就算没有报警也有这条数据。
    '''
    alerts = list()
    if sys.version_info < (3,):
        with open(file_path, 'r') as log_file:
            findFileAlerts(alerts, log_file, prev_time_field, after_lines)
    else:
        with open(file_path, 'r', encoding='utf-8') as log_file:
            findFileAlerts(alerts, log_file, prev_time_field, after_lines)
    return alerts


def buildSavedFileFullPath(log_file_path):
    home = expanduser('~')
    return home + '/' + '.alert_log.' + log_file_path.replace('/', '-').replace('\\', '_').replace(':', '.')


def saveAlerts(log_file_path, alerts):
    '''
    保存alerts信息到隐藏的存储文件（文件名，根据log_file_path自动生成）
    :param log_file_path: 原始日志所在的文件全路径
    :param alerts: 从日志中抽取出的报警信息list，最后一条为上次扫描到的时间点，不带报警信息。
    :return: 无
    '''
    alert_file_path = buildSavedFileFullPath(log_file_path)
    with open(alert_file_path, 'w') as store_file:
        try:
            json.dump(alerts, store_file)
        except Exception as e:
            print(e)


def readPreSavedAlerts(log_file_path):
    '''
    从保存的隐藏文件中（文件名，根据log_file_path自动生成）读取上次报警信息
    :param log_file_path: 原始日志所在的文件全路径
    :return: 报警信息list，最后一条为上次扫描到的时间点，不带报警信息。
    '''
    alert_file_path = buildSavedFileFullPath(log_file_path)
    if os.path.exists(alert_file_path):
        with open(alert_file_path, 'r') as store_file:
            try:
                return json.load(store_file)
            except Exception as e:
                print(e)
    return dict()


if __name__ == '__main__':
    file_path = '/data/temp/alert_log.txt'
    alerts = findAlerts(file_path, '', 3)
    saveAlerts(file_path, alerts)
    alerts1 = readPreSavedAlerts(file_path)
    print(alerts)
    print(json.dumps(alerts1))
    for a in alerts:
        if 'message' in a.keys():
            print(a['message'])
