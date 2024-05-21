import boto3
import requests
import json
from datetime import datetime, timedelta

feishu_url = "https://open.feishu.cn/open-apis/bot/v2/hook/${token}"

data = []

def get_all_cost(start_date, end_date):
    client = boto3.client('ce', region_name='us-east-2')  # 根据您的实际区域选择适当的区域代码
    # 设置查询参数
    query = {
        'TimePeriod': {
            'Start': start_date,
            'End': end_date
        },
        'Granularity': 'MONTHLY',
        'Metrics': ['UnblendedCost'],
        "GroupBy": [
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'  # 按服务进行分组
            },
        ]
    }
    # 发起账单查询请求
    response = client.get_cost_and_usage(**query)
    # 提取费用信息
    results_by_service = response['ResultsByTime'][0]['Groups']
    # 计算总消费金额
    total_cost = 0.0
    for service in results_by_service:
        service_cost = service['Metrics']['UnblendedCost']['Amount']
        total_cost += float(service_cost)
    data.append([{"tag": "text", "text": "Total Amount:  %s  \n" % total_cost}])
    data.append([{"tag": "text", "text": ""}])
    data.append([{"tag": "text", "text": "Top Five List:"}])
    # 提取每个项目和对应的费用数值
    items = [(item, float(item['Metrics']['UnblendedCost']['Amount'])) for item in results_by_service]
    # 根据费用进行排序
    items.sort(key=lambda x: x[1], reverse=True)
    for service in items[:10]:
        service_name = service[0]['Keys'][0]
        service_cost = service[1]
        total_cost += float(service_cost)
        service_cost_f = round(float(service_cost), 2)
        data.append([{"tag": "text", "text": "%s:  %s" % (service_name, service_cost_f)}])
    print(data)


def send_msg(url, cost_data, content):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    payload_message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "AWS %s 消费账单" % cost_data,
                    "content": content
                }
            }
        }
    }
    response = requests.post(url=url, data=json.dumps(payload_message), headers=headers)
    return response


# 获取当前日期
current_date = datetime.now().date()

# 减一天
previous_day = current_date - timedelta(days=1)

# 减两天 能完整查询到的日期
two_days_ago = current_date - timedelta(days=2)

start_date = str(two_days_ago)  # 查询开始日期
end_date = str(previous_day)  # 查询结束日期

get_all_cost(start_date, end_date)
send_msg(feishu_url, two_days_ago, data)
