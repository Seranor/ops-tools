import boto3
import json
import yaml
from config import *
from botocore.exceptions import ClientError
from kubernetes import client, config


# 查看 IAM 中的 oidc
def iam_oidc():
    oidcs = []
    iam_client = boto3.client('iam')
    response = iam_client.list_open_id_connect_providers()
    for provider in response['OpenIDConnectProviderList']:
        oidc = provider['Arn'].split("/", 1)[1]
        oidcs.append(oidc)
    return oidcs


# 创建集群在IAM中的OIDC
def create_oidc():
    iam_client = boto3.client('iam')
    response = iam_client.create_open_id_connect_provider(
        Url='string',
        ClientIDList=[
            'string',
        ],
        ThumbprintList=[
            'string',
        ]
    )


# 查看集群的 oidc 信息
def cluster_oidc(cluster):
    # 创建 EKS 客户端
    eks_client = boto3.client('eks')

    # 获取集群的 OIDC 提供程序配置
    response = eks_client.describe_cluster(
        name=cluster
    )

    oidc = response['cluster']['identity']['oidc']
    return oidc["issuer"].replace('https://', '')


# oidc_provider 对比 返回最终的 OIDC值
def oidc_provider(cluster):
    c_oidc = cluster_oidc(cluster)
    if c_oidc in iam_oidc():
        return c_oidc
    else:
        print(
            "OIDC 未创建，请手动创建OIDC，参考地址: "
            "https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/enable-iam-roles-for-service-accounts.html")
        return


# 创建策略
def policy_create(actions, resources, policy_name):
    iam_client = boto3.client('iam')

    for action in actions:
        policy_document["Statement"][0]['Action'].append(action)

    for resource in resources:
        policy_document["Statement"][0]['Resource'].append(resource)

    # 创建策略
    response = iam_client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_document)
    )

    # 提取创建的策略 ARN
    policy_arn = response['Policy']['Arn']
    try:
        iam_client.get_policy(PolicyArn=policy_arn)
        return policy_arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"The policy with ARN {policy_arn} does not exist.")
            return
        else:
            print("An error occurred:", e)
            return


# 创建Role
def role_create(oidc, ns, sa, role_name, policy_arn):
    iam_client = boto3.client('iam')
    placeholder1 = '$OIDC'  # 占位符
    replacement1 = oidc  # 替换值
    replaced_policy1 = json.dumps(assume_role_policy).replace(placeholder1, replacement1)
    placeholder2 = '$SA'
    replacement2 = f"{ns}:{sa}"
    replaced_policy2 = replaced_policy1.replace(placeholder2, replacement2)

    create_role_response = iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=replaced_policy2
    )
    # 获取角色的 ARN
    role_arn = create_role_response['Role']['Arn']
    try:
        # 获取角色信息
        iam_client.get_role(RoleName=role_name)
        # 将策略绑定到角色
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        return role_arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"The role with ARN {role_name} does not exist.")
            return
        else:
            print("An error occurred:", e)
            return


# 检查角色
def check_role(role_name, role_arn, policy_arn):
    # 创建 IAM 客户端
    iam_client = boto3.client('iam')

    try:
        # 获取角色信息
        response = iam_client.get_role(RoleName=role_name)
        role = response['Role']
        check_role_arn = role['Arn']
        if check_role_arn == role_arn:
            res = iam_client.list_attached_role_policies(RoleName=role_name)
            attached_policies = res['AttachedPolicies']
            if attached_policies:
                for policy in attached_policies:
                    if policy['PolicyArn'] == policy_arn:
                        return True
                    else:
                        print("policy_arn inconsistent")
                        return False
            else:
                print(f"No attached policies found for role '{role_name}'.")
                return False
        else:
            print("role_arn inconsistent")
            return False
    except iam_client.exceptions.NoSuchEntityException:
        print(f"The role with ARN '{role_name}' does not exist.")
        return False


# 创建ServiceAccount
def create_sa(ns, sa, role_arn, eks_arn):
    # 解析 YAML 并创建 Kubernetes 对象
    sa_yaml = yaml_sa_template % (sa, ns, role_arn)
    yaml_obj = yaml.safe_load(sa_yaml)
    metadata = client.V1ObjectMeta(**yaml_obj['metadata'])
    service_account = client.V1ServiceAccount(metadata=metadata)

    # 创建 Kubernetes 对象
    config.load_kube_config(context=eks_arn)
    k8s_client = client.ApiClient()
    api_instance = client.CoreV1Api(k8s_client)
    try:
        api_instance.create_namespaced_service_account(
            body=service_account,
            namespace=ns
        )
        print(f"{sa} ServiceAccount created successfully.")
    except client.exceptions.ApiException as e:
        print(f"Exception when creating ServiceAccount: {e}")

