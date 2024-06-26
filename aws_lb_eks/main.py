from aws_lb import get_load_balancers
from eks_lb import get_load_balancer_external_ips


def find_discrepancies(array1, array2):
    set1 = set(array1)
    set2 = set(array2)
    only_in_array1 = set1 - set2
    only_in_array2 = set2 - set1
    return list(only_in_array1), list(only_in_array2)


region = 'us-east-2'
access_key = '$ACCESS'
secret_key = '$KEY'

clusters = {
    "xx-staging": "arn:aws:eks:us-east-2:888888888888:cluster/xx-staging",
    "aa-staging": "arn:aws:eks:us-east-2:888888888888:cluster/aa-staging"
}

aws_load_balancers = get_load_balancers(region, access_key, secret_key)

eks_lbs = []
for cluster_name, cluster_arn in clusters.items():
    service_ips = get_load_balancer_external_ips(cluster_arn)

    if service_ips:
        for service_name, namespace, external_ip in service_ips:
            eks_lbs.append(external_ip)
    else:
        print("No LoadBalancer services found.")

only_in_aws, only_in_eks = find_discrepancies(aws_load_balancers, eks_lbs)
print("Only in AWS:", only_in_aws)
print("Only in EKS:", only_in_eks)