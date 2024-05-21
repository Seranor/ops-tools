import sys
from aws_tools import *
from config import *

policy_name = app_name + "-policy"
role_name = app_name + "-Role"
sa_name = app_name + "-sa"

if __name__ == '__main__':
    oidc = oidc_provider(EKS_CLUSTER)
    if oidc:
        pass
    else:
        sys.exit(1)

    policy_arn = policy_create(Action, Resource, policy_name)
    if policy_arn:
        print(f"{policy_name} 创建成功 Arn为 --> {policy_arn}")
    else:
        print(f"{policy_arn}  创建失败")
        sys.exit(2)

    role_arn = role_create(oidc, namespace, sa_name, role_name, policy_arn)
    if role_arn:
        print(f"{role_name} 创建成功 Arn为 --> {role_arn}")
    else:
        print(f"{role_name} 创建失败")
        sys.exit(3)

    check_res = check_role(role_name, role_arn, policy_arn)
    if check_res:
        print("检查Role 和 Policy 成功")
    else:
        print("检查Role 和 Policy 失败")
        sys.exit(3)

    create_sa(namespace, sa_name, role_arn, EKS_ARN)

