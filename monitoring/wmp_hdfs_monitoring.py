#!/usr/bin/python3
# coding=utf-8

import requests
import smtplib
import json
import sys
from datetime import datetime
from pytz import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print("""
### HDFS Monitoring Mailer ###

** Python 3 or Higher
** Dependencies Package
    - requests(REST API Library) : pip install requests
    - requests(REST API Library) : pip install pytz
** Usage
    1. HDFS 모니터링 할 Ambari의 서버명 혹은 아이피와 계정, 패스워드를 입력한다.
        ex:) python3 wmp_hdfs_monitoring.py '{ambari_id}' '{ambari_pw}'
    2. 모니터링 정보는 개인화플랫폼개발팀에게 메일로 전송된다.
    3. 모든 Cluster 중 단 한개라도 문제가 있으면 위험, 디스크사용량이 70프로 이상이면 경고, 80프로 이상이면 위험
""")

if len(sys.argv) != 4:
    print("usage : python3 wmp_hdfs_monitoring.py '{ambari_id}' '{ambari_pw}' {cluster_name}")
    sys.exit(-1)

id = sys.argv[1]
pw = sys.argv[2]
name = sys.argv[3]

now = datetime.now(timezone('Asia/Seoul')).strftime("%H%M")

def send_email(subject, msg, to_addr):
    from_addr = 'kwangjin@wemakeprice.com'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login("cloudapps@wemakeprice.com", 'xmrrkeovy123!@#')

    body = MIMEMultipart()
    body['Subject'] = subject
    body['From'] = from_addr
    body['To'] = to_addr

    html = "<div><pre>" + msg + "</pre></div>"
    msg = MIMEText(html, 'html')
    body.attach(msg)
    tolist = to_addr.split(",")

    server.sendmail(from_addr, tolist, body.as_string())
    server.quit();

def unit_conversion(number_of_bytes):
    if number_of_bytes < 0:
        raise ValueError("number_of_bytes can't be smaller than 0")

    step_to_greater_unit = 1024.
    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'
    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)

    return str(number_of_bytes) + ' ' + unit

# get ClusterName
clusterInfo = requests.get("http://localhost:8080/api/v1/clusters", auth=(id, pw))
if clusterInfo.status_code != 200:
    print(clusterInfo.status_code)
cl = clusterInfo.json()
cluster = cl["items"][0]["Clusters"]["cluster_name"]

# get HostName
hostList = list()
hostURL = "http://localhost:8080/api/v1/clusters/%s/hosts" % cluster
hosts = requests.get(hostURL, auth=(id, pw))
hostInfo = hosts.json()
for host in hostInfo["items"]:
    hostList.append(host["Hosts"]["host_name"])

# get HDFS Metrics
hdfsURL = "http://localhost:8080/api/v1/clusters/%s/services/HDFS/components/NAMENODE" % cluster
print("Connect Rest API URL: %s" % hdfsURL)

hdfsInfo = requests.get(hdfsURL, auth=(id, pw))
if hdfsInfo.status_code != 200:
    print(hdfsInfo.status_code)
    sys.exit(-1)

# Reload 처음 로드 값과 두번째 로드 값이 다름
hdfsInfo = requests.get(hdfsURL, auth=(id, pw))
if hdfsInfo.status_code != 200:
    print(hdfsInfo.status_code)
    sys.exit(-1)

# get YARN Metrics
yarnURL = "http://localhost:8080/api/v1/clusters/%s/services/YARN/components/RESOURCEMANAGER" % cluster
print("Connect Rest API URL: %s" % yarnURL)

# Status (모든 Cluster 중 단 한개라도 문제가 있으면 위험, 디스크사용량이 70프로 이상이면 경고, 80프로 이상이면 위험)
status = "정상"
bf = ''

# get Local Disk Usage
bf += "<strong>Host Info</strong>\n"
for host in hostList:
    hostURL = "http://localhost:8080/api/v1/clusters/{0}/hosts/{1}".format(cluster, host)
    hostMetrics = requests.get(hostURL, auth=(id, pw))
    hostInfo = hostMetrics.json()

    free = hostInfo["metrics"]["disk"]["disk_free"]
    total = hostInfo["metrics"]["disk"]["disk_total"]
    per = round((total - free) / total * 100, 2)
    bf += "<strong>HostName         : %s</strong>\n" % host
    bf += "Host Disk Total  : %s GB\n" % total
    bf += "Host Disk Free   : %s GB\n" % free
    bf += "Host Disk Usage  : {0} GB ({1}%)\n".format(round(total-free, 2), per)

    if per in range(70, 80):
        bf += "<strong>%s 디스크 사용량이 높습니다.</strong>\n" % host
        if status == "정상":
            status = "경고"
    elif per >= 80:
        bf += "<strong>%s 디스크 사용량이 높습니다.</strong>\n" % host
        if status == "정상":
            status = "위험"
    bf += "\n"

# NameNode parsing
nn = hdfsInfo.json()
nn_Safemode = "정상" if len(nn["ServiceComponentInfo"]["Safemode"]) == 0 else "비정상: " + nn["ServiceComponentInfo"]["Safemode"]
nn_DeadNodes = "정상" if nn["ServiceComponentInfo"]["DeadNodes"] == "{}" else "비정상: " + nn["ServiceComponentInfo"]["DeadNodes"]
nn_DecomNodes = "정상" if nn["ServiceComponentInfo"]["DecomNodes"] == "{}" else "비정상: " + nn["ServiceComponentInfo"]["DecomNodes"]
nn_HeapMemoryMax = unit_conversion(nn["ServiceComponentInfo"]["HeapMemoryMax"])
nn_HeapMemoryUsed = unit_conversion(nn["ServiceComponentInfo"]["HeapMemoryUsed"])
nn_StartTime = datetime.fromtimestamp(int(nn["ServiceComponentInfo"]["StartTime"] / 1000))
nn_NonDfsUsedSpace = unit_conversion(nn["ServiceComponentInfo"]["NonDfsUsedSpace"])
nn_CapacityTotalGB = nn["metrics"]["dfs"]["FSNamesystem"]["CapacityTotalGB"]
nn_CapacityUsedGB = nn["metrics"]["dfs"]["FSNamesystem"]["CapacityUsedGB"]
nn_PercentRemaining = round(nn["ServiceComponentInfo"]["PercentRemaining"], 2)
nn_PercentUsed = round(nn["ServiceComponentInfo"]["PercentUsed"], 2)
nn_UnderReplicatedBlocks = nn["metrics"]["dfs"]["FSNamesystem"]["UnderReplicatedBlocks"]
nn_CorruptBlocks = nn["metrics"]["dfs"]["FSNamesystem"]["CorruptBlocks"]
nn_MissingBlocks = nn["metrics"]["dfs"]["FSNamesystem"]["MissingBlocks"]

if nn_PercentUsed in range(70, 80):
    if status == "정상":
        status = "경고"
elif nn_PercentUsed >= 80:
    if status == "정상" or status == "경고":
        status = "위험"

if nn_Safemode != "정상" or nn_DeadNodes != "정상" or nn_DecomNodes != "정상":
    bf += "<strong>HDFS 점검이 필요합니다.</strong>\n"
    if status == "정상" or status == "경고":
        status = "위험"

if nn_PercentUsed >= 70:
    bf += "<strong>HDFS 디스크 사용량이 높습니다.</strong>\n"
    bf += "\n"
    if status == "정상":
        status = "경고"

bf += "<strong>NameNode Info</strong>\n"
bf += "SafeMode            : %s\n" % nn_Safemode
bf += "Dead Nodes          : %s\n" % nn_DeadNodes
bf += "Decommission Nodes  : %s\n" % nn_DecomNodes
bf += "Heap Memory Max     : %s\n" % nn_HeapMemoryMax
bf += "Heap Memory Used    : %s\n" % nn_HeapMemoryUsed
bf += "Start Time          : %s\n" % nn_StartTime
bf += "Non DFS Used        : %s\n" % nn_NonDfsUsedSpace
bf += "<strong>DFS Total           : %s GB</strong>\n" % nn_CapacityTotalGB
bf += "<strong>DFS Used            : %s GB</strong>\n" % nn_CapacityUsedGB
bf += "<strong>DFS Remaining       : %s%%</strong>\n" % nn_PercentRemaining
bf += "<strong>DFS Used            : %s%%</strong>\n" % nn_PercentUsed
bf += "Under replicated blocks      : %s\n" % nn_UnderReplicatedBlocks
bf += "Blocks with corrupt replicas : %s\n" % nn_CorruptBlocks
bf += "Missing blocks               : %s\n" % nn_MissingBlocks
bf += "\n"

# DataNode parsing
bf += "<strong>DataNode Info</strong>\n"
dn = json.loads(nn["ServiceComponentInfo"]["LiveNodes"])
sortedKeys = sorted(dn.keys())
for cluster in sortedKeys:
    dn_adminState = "정상" if dn[cluster]["adminState"] == "In Service" else "비정상"
    dn_nonDfsUsedSpace = unit_conversion(dn[cluster]["nonDfsUsedSpace"])
    dn_capacity = unit_conversion(dn[cluster]["capacity"])
    dn_usedSpace = unit_conversion(dn[cluster]["usedSpace"])
    dn_remaining = unit_conversion(dn[cluster]["remaining"])

    if dn_adminState != "정상":
        if status == "정상" or status == "경고":
            status = "위험"

    bf += "<strong>HostName        : %s</strong>\n" % cluster.replace(":50010", "")
    bf += "Status          : %s\n" % dn_adminState
    bf += "Non DFS Used    : %s\n" % dn_nonDfsUsedSpace
    bf += "DFS Total       : %s\n" % dn_capacity
    bf += "DFS Used        : %s\n" % dn_usedSpace
    bf += "DFS Remaining   : %s\n" % dn_remaining
    bf += "\n"

# DataNode Fail
if nn_DecomNodes != "정상":
    dn_fail = json.loads(nn["ServiceComponentInfo"]["DeadNodes"])
    sortedKeys = sorted(dn_fail.keys())
    for cluster in sortedKeys:
        bf += "<strong>DataNode Cluster: %s</strong>\n" % cluster.replace(":50010", "")
        bf += "Status          : 비정상\n"
        bf += "\n"

yarnInfo = requests.get(yarnURL, auth=(id, pw))
if yarnInfo.status_code != 200:
    print(yarnInfo.status_code)
    sys.exit(-1)

# Reload
yarnInfo = requests.get(yarnURL, auth=(id, pw))
if yarnInfo.status_code != 200:
    print(yarnInfo.status_code)
    sys.exit(-1)

yn = yarnInfo.json()
decommissionedNMcount = yn["ServiceComponentInfo"]["rm_metrics"]["cluster"]["decommissionedNMcount"]
lostNMcount = yn["ServiceComponentInfo"]["rm_metrics"]["cluster"]["lostNMcount"]

if decommissionedNMcount + lostNMcount > 0:
    bf += "<strong>리스트에 누락된 Node Manager 점검이 필요합니다.</strong>\n"
    bf += "\n"
    if status == "정상" or status == "경고":
        status = "위험"

nodeManager = json.loads(yn["ServiceComponentInfo"]["rm_metrics"]["cluster"]["nodeManagers"])
sortedNodeManager = sorted(nodeManager, key=lambda x: x["HostName"])
bf += "<strong>NodeManager Info</strong>\n"
for nm in sortedNodeManager:
    nm_host = nm["HostName"]
    nm_state = "정상" if nm["State"] == "RUNNING" else "비정상"
    bf += "<strong>HostName         : %s</strong>\n" % nm_host
    bf += "State            : %s\n" % nm_state

if nm_state == "비정상":
    if status == "정상" or status == "경고":
        status == "위험"

# 조건 별 Mailing 1. 클러스터 상태가 정상이 아닌 경우 2. 9시30분/17시30분 정기메일
toEmail = 'kwangjin@wemakeprice.com'

if status == "위험" or now == "0930" or now == "1730":
    send_email("[%s 모니터링 결과: %s] %s HDFS 상세현황" % (name, status, datetime.now().strftime('%Y년 %m월 %d일 %H시')), bf, toEmail)

print("Complete Job")