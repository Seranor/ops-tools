import boto3


def get_load_balancers(region, access_key, secret_key):
    lbs = []

    # 创建 ELB 的客户端
    elb_client = boto3.client('elb', region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    # 查询所有 Classic Load Balancers
    response_classic = elb_client.describe_load_balancers()

    # 收集 Classic Load Balancer 的 DNS 名称
    for lb in response_classic['LoadBalancerDescriptions']:
        lbs.append(lb['DNSName'])

    # 创建 ELBv2 的客户端
    elbv2_client = boto3.client('elbv2', region_name=region, aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key)

    # 查询所有 Application Load Balancers
    response_application = elbv2_client.describe_load_balancers()

    # 收集 Application Load Balancer 的 DNS 名称
    for lb in response_application['LoadBalancers']:
        lbs.append(lb['DNSName'])

    return lbs