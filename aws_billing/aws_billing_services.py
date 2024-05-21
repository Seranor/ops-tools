import boto3
import requests
import json
from datetime import datetime, timedelta

feishu_url = "https://open.feishu.cn/open-apis/bot/v2/hook/${token}"
threshold_amount = "180"
data = []
services_name = {
    "Amazon Neptune": "180",
    "Amazon Redshift": "50",
}


def get_server_cost(start_date, end_date, server_name):
    client = boto3.client('ce', region_name='us-east-2')
    # 设置查询参数
    query = {
        'TimePeriod': {
            'Start': start_date,
            'End': end_date
        },
        'Granularity': 'MONTHLY',
        'Metrics': ['UnblendedCost'],
        'Filter': {
            'Dimensions': {
                'Key': 'SERVICE',
                'Values': [server_name]
            }
        }
    }
    # 发起查询请求
    response = client.get_cost_and_usage(**query)

    # 提取费用金额
    results = response['ResultsByTime']
    if len(results) > 0:
        # amount = results[0]['Total']['UnblendedCost']['Amount']
        # unit = results[0]['Total']['UnblendedCost']['Unit']
        return results
    else:
        return


def send_msg(url, content):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    payload_message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "Neptune消费超过阈值告警",
                    "content": content
                }
            }
        }
    }
    response = requests.post(url=url, data=json.dumps(payload_message), headers=headers)
    return response.json


# 获取当前日期
current_date = datetime.now().date()

# 减一天
previous_day = current_date - timedelta(days=1)

# 减两天 能完整查询到的日期
two_days_ago = current_date - timedelta(days=2)

start_date = str(two_days_ago)  # 查询开始日期
end_date = str(previous_day)  # 查询结束日期

for name in services_name:
    cost_res = get_server_cost(start_date, end_date, name)
    if cost_res:
        amount = round(float(cost_res[0]['Total']['UnblendedCost']['Amount']), 2)
        unit = cost_res[0]['Total']['UnblendedCost']['Unit']
        print(f"账单日期: {start_date} 服务名称: {name} 消费金额: {amount} {unit}")
        if amount > float(services_name.get(name)):
            data.append([{"tag": "text", "text": "账单日期: %s" % start_date}])
            data.append([{"tag": "text", "text": "服务名称: %s" % name}])
            data.append([{"tag": "text", "text": "消费金额: %s %s" % (round(float(amount), 2), unit)}])
            data.append([{"tag": "at", "user_id": "all"}])
            send_msg(feishu_url, data)
    else:
        print("服务账单错误")
