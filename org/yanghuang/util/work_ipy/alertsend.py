# coding=UTF-8

import alertsnap
import sys
import urllib

def createAlertMsg(alert:dict,host_name,host_ip,)->dict:
    msg=dict()
    msg['type']='Alert'
    msg['service']='DMP ping'
    msg['state'] = 'CRITICAL'
    msg['source']='39'
    msg['host']=host_name
    msg['address']=host_ip
    msg['additional']=alert['message']
    return msg

if __name__=='__main__':
    # 读取命令行参数
    log_file_path=sys.argv[1]
    host_name=sys.argv[2]
    host_ip=sys.argv[3]
    post_url=sys.argv[4]
    max_alert_num=3
    if len(sys.argv)>=6:
        max_alert_num=int(sys.argv[5])
    # 从文件中读取上次报警检查到的时间点
    preAlerts=alertsnap.readPreSavedAlerts(log_file_path)
    pre_time_field=''
    if len(preAlerts) > 0:
        lasted_alert=preAlerts.pop()
        pre_time_field=lasted_alert['ts']
    print(pre_time_field)
    alerts=alertsnap.findAlerts(log_file_path,pre_time_field)
    # 根据参数，生成最多报警列表
    post_alerts=list()
    if len(alerts)<=max_alert_num+1:
        post_alerts=alerts
    else:
        for i in range(len(alerts)-(max_alert_num+1),len(alerts)):
            post_alerts.append(alerts[i])
    # 发送报警信息到指定url
    try:
        for a in post_alerts:
            if 'message' in a.keys():
                msg=createAlertMsg(a,host_name,host_ip)
                params = urllib.urlencode(msg)
                p=urllib.open(post_url,params)
                p.read()
        alertsnap.saveAlerts(log_file_path,post_alerts)
    except Exception as e:
        print(e)
    print(post_alerts)