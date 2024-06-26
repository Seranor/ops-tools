from kubernetes import client, config


def get_load_balancer_external_ips(cluster_arn):
    config.load_kube_config(context=cluster_arn)
    v1 = client.CoreV1Api()

    service_ips = []
    service_list = v1.list_service_for_all_namespaces(watch=False)

    for service in service_list.items:
        if service.spec.type == "LoadBalancer":
            for lb_status in service.status.load_balancer.ingress:
                service_ips.append((service.metadata.name, service.metadata.namespace, lb_status.hostname))

    return service_ips