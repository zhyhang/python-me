# coding=UTF-8

import json
import os
import io
import re
from os.path import expanduser
from typing import TextIO

# 最大内存持有报警条数，避免内存占用过多
maxAlertsInMem = 1000
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


def isTimeLine(line_splits: list) -> bool:
    if line_splits == None or len(line_splits) == 0:
        return False
    if dateTimePattern.match(line_splits[0]):
        return True
    else:
        return False


def isLogLevelLine(line_splits: list, level: str) -> bool:
    if line_splits == None or len(line_splits) < 2:
        return False
    if level == line_splits[1].upper():
        return True
    else:
        return False


def isErrorLine(line_splits: list) -> bool:
    return isLogLevelLine(line_splits, alertLevelError)


def isWarnLine(line_splits: list) -> bool:
    return isLogLevelLine(line_splits, alertLevelWarn)


def isInfoLine(line_splits: list) -> bool:
    return isLogLevelLine(line_splits, alertLevelINFO)


def isExceptionLine(line_splits: list) -> bool:
    if line_splits == None or len(line_splits) < 3:
        return False
    for i in range(2, len(line_splits)):
        if alertKeywordsException in line_splits[i].lower():
            return True
    return False


def isFatalLine(line_splits: list) -> bool:
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


def findFileAlerts(alerts: list, log_file: TextIO, prev_time_field: str, after_lines: int) -> None:
    msg_line_count = 0
    latest_time_field = ''
    for line in log_file:
        line_splits = line.split(fieldSeparator)
        if msg_line_count > 0 and msg_line_count < after_lines + 1:
            if not isTimeLine(line_splits):
                msg_line_count += 1
                alerts[len(alerts) - 1][alertJsonKeyMsg] += line
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


def findAlerts(file_path: str, prev_time_field: str, after_lines=2) -> list:
    '''
    在传入的文件中查询报错日志信息，组织为json列表。
    :param file_path: 日志文件路径
    :param prev_time_field: 上次已经报警的最后时间字串，格式为'[2020-03-24 20:21:22.023'
    :param after_lines: 报警行，再取后续行数
    :return: 报警信息列表，列表元素为：['ts']=报警时间，格式为'[2020-03-24 20:21:22.023';['message']=详细信息。
    最后一条数据不带message信息，只带ts，用于标识日志文件扫描到的时间点，就算没有报警也有这条数据。
    '''
    alerts = list()
    with io.open(file_path, encoding='utf-8') as log_file:
        prev_time_str = ''
        if prev_time_field != None:
            prev_time_str = prev_time_field
        findFileAlerts(alerts, log_file, prev_time_str, after_lines)
    return alerts


def buildSavedFileFullPath(log_file_path: str) -> str:
    home = expanduser('~')
    return home + '/' + '.alert_log.' + log_file_path.replace('/', '-').replace('\\', '_').replace(':', '.')


def saveAlerts(log_file_path: str, alerts: list):
    alert_file_path = buildSavedFileFullPath(log_file_path)
    with io.open(alert_file_path, 'wb') as store_file:
        try:
            store_file.write(json.dumps(alerts, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(e)


def readPreSavedAlerts(log_file_path: str) -> dict:
    alert_file_path = buildSavedFileFullPath(log_file_path)
    if os.path.exists(alert_file_path):
        with io.open(alert_file_path, 'r', encoding='utf-8') as store_file:
            try:
                return json.load(store_file)
            except Exception as e:
                print(e)
    return dict()


if __name__ == '__main__':
    line = '[2020-03-24][ERROR][ID]: fatal error, NullPointException'
    print(isExceptionLine(line.split('][')))
    file_path = '/temp/alert_log.txt'
    alerts = findAlerts(file_path, '', 3)
    saveAlerts(file_path, alerts)
    # alerts1=readPreSavedAlerts(file_path)
    print(alerts)
