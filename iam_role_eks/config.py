# aws基础信息
EKS_CLUSTER = "app-staging"
AWS_REGION = "us-east-2"
ACCOUNT_ID = "8888888"
EKS_ARN = '$ARN'

# 集群信息
namespace = "app-dev"
app_name = "dev-test-service"

# 权限相关
Action = [
        "secretsmanager:ListSecretVersionIds"
]

Resource = [
        "$ARN",
]

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [],
            "Resource": []
        }
    ]
}

assume_role_policy = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'Federated': 'arn:aws:iam::881328871944:oidc-provider/$OIDC'
            },
            'Action': 'sts:AssumeRoleWithWebIdentity',
            'Condition': {
                'StringEquals': {
                    '$OIDC:aud': 'sts.amazonaws.com',
                    '$OIDC:sub': 'system:serviceaccount:$SA'
                }
            }
        }
    ]
}

yaml_sa_template = """
apiVersion: v1
kind: ServiceAccount
metadata:
  name: %s
  namespace: %s
  annotations:
    eks.amazonaws.com/role-arn: %s
"""

'''
# 创建 STS 客户端
sts_client = boto3.client('sts')

# 获取当前账户的账户 ID
response = sts_client.get_caller_identity()
account_id = response['Account']

print("当前账户的账户 ID：", account_id)
'''

