# aws_billing
说明: 
aws_billing_all.py  
获取aws头两天的消费总额(时区原因，当天只能获取到前天的完整账单) 进行飞书通知

aws_billing_services.py
根据设定服务名称和阈值金额进行通知，当设定的服务超过设定的金额进行通知

### 运行条件
```bash
# 需要使用 aws 命令
# aws 命令安装
https://docs.aws.amazon.com/zh_cn/cli/latest/userguide/getting-started-install.html

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip

sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update

# 配置凭证
aws configure

# 通知设置
feishu_url 自行配置机器人地址

# aws_billing_service
services_name = {
    "Amazon Neptune": "180",  # 单独设置 服务名称和超额告警金额
    "Amazon Redshift": "50",
}

```

### 运行
```bash
pip install -r requirements.txt

python aws_billing_all.py  
python aws_billing_services.py
```

# aws_lb_eks
说明：EKS 集群上创建的 Loadbancer 会有没有回收的情况，

这个工具对比 AWS 和 EKS 的 LB，一般是 AWS 的 LB 会比 EKS 上的多，人工确认是否可以删除
```bash
# 下载依赖
pip install -r requirements.txt

# 编辑 main.py
修改 
region
access_key
secret_key
clusters

确保填写的用户key有权限

# 执行脚本
python3 main.py

出现的结果是Loadbancer的domain，拿着domain去AWS上查找是否还在使用，再进行删除
```

# cloudflare_dns
说明:
命令实现在cloudflare查看，添加，更新DNS信息


### 运行
```bash
# 下载依赖
pip install -r requirements.txt

# 通过 --help 查看参数
# -e 参数和 -t 参数可以通过设置环境变量传入
export CF_EMAIL=xxxx
export CF_TOKEN=xxxx
# 设置环境变量后就不需要传入 -e -t 参数

python main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  A command CloudFlare add get update DNS.

Options:
  -e, --email TEXT      Email address
  -t, --token TEXT      CloudFlare Token
  -d, --domain TEXT     Domain name
  -s, --subdomain TEXT  Subdomain name
  --help                Show this message and exit.

Commands:
  add-dns
  get-dns
  update-dns

# get-dns 和 update-dns 还有参数
python main.py update-dns --help
Usage: main.py update-dns [OPTIONS]

Options:
  --dnstype TEXT            DNS TYPE exp: A, CNAME, TXT
  -cont, --content TEXT     DNS resolution address
  --proxied / --no-proxied  Whether the DNS record is proxied
  --help                    Show this message and exit.
```



# iam_role_eks
说明:
创建 EKS 中应用运行所需要在 AWS 的权限，并创建 serviceaccount

例如：file-service 需要 AWS 中 s3 某个存储桶的权限，

      创建 policy
      创建 role --> 信任主体设置为EKS集群下namespace的serviceaccount
      然后 role 绑定 policy 实现 AWS 的 Role 权限和 EKS集群的 serviceaccount 进行绑定

### 设置
```bash
# 前置条件
1.配置aws认证
2.设置kubernetes的contexts


# 主要设置 config.py 文件
# 修改以下信息即可 

# aws基础信息
EKS_CLUSTER = "app-staging"
AWS_REGION = "us-east-2"
ACCOUNT_ID = "881328871944"
EKS_ARN = 'arn:aws:eks:us-east-2:881328871944:cluster/app-staging'

# 集群信息
namespace = "app-development"
app_name = "dev-hermes-service"   # 生成的 sa 名称就会是 dev-hermes-service-sa      

# 权限相关  可以设置不同种类的权限和 ARN 他们会自行进行绑定
Action = [
        "s3:xxx",
        "secretsmanager:xxx"
]

Resource = [
        "secretsmanager ARN",
        "s3 ARN"
]
```

### 运行
```bash
pip install -r requirements.txt

python main.py

# 最后会生成一个 serviceaccount 自行进行绑定
```


# pre_control
说明:
开启、关闭、查看DocumentDB、RDS集群和EKS集群
(PRE 环境的开启关闭查看)

```bash
# 查看状态
curl --location '127.0.0.1:5000/api/v1/pre/status'

# 开启集群
curl --location --request POST '127.0.0.1:5000/api/v1/pre/start'

# 关闭集群
curl --location --request POST '127.0.0.1:5000/api/v1/pre/stop'
```

### 环境变量
```bash
AWS_REGION=us-east-2
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
EKS_CLUSTER_NAME=app-pre
DOCDB_CLUSTER_NAME=predb
RDS_CLUSTER_NAME=pre
EKS_NODE_GROUPS = {"pool-02":1,"pool-03":2}

EKS_CLUSTER_NAME    # EKS 集群名称
EKS_NODE_GROUPS     # EKS 节点组名称和希望开启的数量
DOCDB_CLUSTER_NAME  # DocumentDB 集群名称
RDS_CLUSTER_NAME    # RDS 集群名称
```

### 运行
```bash
版本 python 3.11

pip install -r requirements.txt

python run.py
```

# update_image
说明: 
根据 update-version.yaml 中的更新信息进行替换镜像版本

前置条件
1.配置aws认证
2.设置kubernetes的contexts

### yaml说明
```bash
- cluster: "contexts"        # k8s contexts 
  namespace: "app-dev"       # namespace
  registry: "hub.xxx.com"    # registry address
- app:
  - imageName: xxxx-service-all-be # image name
    version: v2.6.2                # vrsion 
    isUpdate: true                 # update on
    appList:
      - xxx-service-be             # deployment 1
      - xxx-kafka-consume-be       # deployment 2
```


### 运行
```bash
pip install -r requirements.txt

# 查看帮助
python main.py --help
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  A command line tool for getting info and updating kubernetes deployment
  image.

Options:
  --help  Show this message and exit.

Commands:
  get-info        # 查看要更新应用的名称 镜像 版本 更新版本
  update-image    # 按照 update-version.yaml 的内容进行替换脚本
  rest-info       # 重置 update-version.yaml 的 isUpdate 为 false

# 参数说明
--file 或者 -f 文件路径，默认是 update-version.yaml

rest-info
# 运行结果会进行记录
info-get-20240425-07-06.txt    # 直接获取的信息
info-update-20240425-07-25.txt # 更新前获取的信息  
```