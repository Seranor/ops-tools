import logging
from kubernetes import client, config

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_deployment_image(cluster, namespace, deployment_name, new_image):
    # 加载 Kubernetes 配置
    config.load_kube_config(context=cluster)

    # 创建 Kubernetes 客户端 API 实例
    apps_v1_api = client.AppsV1Api()

    # 获取指定名称的 Deployment 对象
    deployment = apps_v1_api.read_namespaced_deployment(deployment_name, namespace)

    # 更新 Deployment 中所有容器的镜像版本
    for container in deployment.spec.template.spec.containers:
        container.image = new_image
    # 输出日志
    logger.info(f"Updating image of deployment '{deployment_name}' in namespace '{namespace}' to '{new_image}'")

    # 应用更新
    apps_v1_api.patch_namespaced_deployment(deployment_name, namespace, deployment)


