# coding=UTF-8

'''
send alert to monitor service

- deploy tailer.py, alertsnap2.py and alertsend-saicmotor2.py to a dir e.g. /data/dmp/monitor/

- crontab -e
- */10 * * * * /usr/bin/python2.7 /data/dmp/monitor/alertsend-saicmotor2.py log_file_full_path host_name host_ip service_url
- every 10 minute to scan the log file from last scanned timestamp in tail 500000 lines
- default max send alerts is 10, can specify it at last parameter in above command

- default scan max tail 500000 lines (in alertsnap2.py)
- default place max 1000 alerts in memory(in alertsnap2.py)

- previous successfully sent alerts saved in ~/.alert_log.log_full_path which holds the alerts and latest scanned timestamp
- if delete the file, next running will scan log file from head again.
- you can update the last record timestamp to move next scan lines.

'''

import alertsnap2
import sys
import json

if sys.version_info < (3,):
    import urllib2
    import urllib
else:
    import urllib.request
    import urllib.parse

# 上汽的参数名
serviceUrlParamName = 'eventRequest'


def createAlertMsg(alert, host_name, host_ip):
    msg = dict()
    msg['type'] = 'Alert'
    msg['service'] = 'DMP ping'
    msg['state'] = 'CRITICAL'
    msg['source'] = '39'
    msg['host'] = host_name
    msg['address'] = host_ip
    msg['additional'] = alert['message']
    return msg


def requestService2():
    full_url = service_url + '?' + urllib.urlencode(msg_with_query_para)
    response = urllib2.urlopen(urllib2.Request(url=full_url))
    response.read()


def requestService3():
    full_url = service_url + '?' + urllib.parse.urlencode(msg_with_query_para)
    response = urllib.request.urlopen(url=full_url)
    response.read()


if __name__ == '__main__':
    # 读取命令行参数
    log_file_path = sys.argv[1]
    host_name = sys.argv[2]
    host_ip = sys.argv[3]
    service_url = sys.argv[4]
    max_alert_num = 10
    if len(sys.argv) >= 6:
        max_alert_num = int(sys.argv[5])
    # 从文件中读取上次报警检查到的时间点
    preAlerts = alertsnap2.readPreSavedAlerts(log_file_path)
    pre_time_field = ''
    if len(preAlerts) > 0:
        latest_alert = preAlerts.pop()
        pre_time_field = latest_alert['ts']
    alerts = alertsnap2.findAlerts(log_file_path, pre_time_field)
    # 根据参数，生成最多报警列表
    sending_alerts = list()
    if len(alerts) <= max_alert_num + 1:
        sending_alerts = alerts
    else:
        for i in range(len(alerts) - (max_alert_num + 1), len(alerts)):
            sending_alerts.append(alerts[i])
    # 发送报警信息到指定url
    try:
        for a in sending_alerts:
            if 'message' in a.keys():
                msg = createAlertMsg(a, host_name, host_ip)
                msg_with_query_para = dict()
                msg_with_query_para[serviceUrlParamName] = json.dumps(msg)
                if sys.version_info < (3,):
                    requestService2()
                else:
                    requestService3()
        # 发送成功保存消息，下次扫描从新时间点开始
        alertsnap2.saveAlerts(log_file_path, sending_alerts)
    except Exception as e:
        print(e)
