from datetime import datetime
from rich.table import Table
from rich.console import Console
from kubernetes import client, config


def get_deployments(cluster, namespace, name):
    config.load_kube_config(context=cluster)  # 从 kubeconfig 文件加载 Kubernetes 配置
    api_instance = client.AppsV1Api()

    try:
        deployment = api_instance.read_namespaced_deployment(name, namespace)
        spec = deployment.spec
        containers = spec.template.spec.containers
        for container in containers:
            image = container.image
            image_parts = image.split(":")
            if len(image_parts) == 2:
                image_name, image_version = image_parts
            else:
                image_name = image
                image_version = "unknown"
            image_name = image_name.split("/")[-1]  # 去掉仓库名称
        return {"image_name": image_name, "image_version": image_version}
    except Exception as e:
        return None


def out_info(cluster, namespace, apps_info, way):
    # 创建 Rich 的 Console 对象
    console = Console()

    # 创建 Rich 的 Table 对象
    table = Table(title="Deployment Information", show_header=True, header_style="bold magenta")

    # 添加表头
    table.add_column("Deployment", style="cyan")
    table.add_column("Image Name", style="green")
    table.add_column("Current Version", style="yellow")
    table.add_column("Upgrade Name", style="blue")

    for app_info in apps_info:
        if app_info.get('isUpdate') == True:
            for app_name in app_info.get('appList'):
                image_info = get_deployments(cluster, namespace, app_name)
                if image_info:
                    table.add_row(app_name, image_info.get("image_name"), image_info.get("image_version"),
                                  app_info.get('version'))
                else:
                    print(f"Deployment '{app_name}' not found in namespace '{namespace}'.")

    # 输出表格
    console.print(table)
    file_name = f"info-{way}-{datetime.now().strftime('%Y%m%d-%H-%M')}.txt"
    # 将表格内容打印到标准输出流，并通过重定向将输出写入文件
    with open(file_name, "w", encoding="utf-8") as f:
        with console.capture() as capture:
            console.print(table)

        f.write(capture.get())


if __name__ == '__main__':
    import yaml

    file = "update-version.yaml"
    data = yaml.safe_load(open(file))
    cluster = data[0]["cluster"]
    namespace = data[0]["namespace"]
    apps_info = data[1].get('app')

    out_info(cluster, namespace, apps_info, way="get")

