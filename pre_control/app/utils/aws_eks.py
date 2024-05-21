import boto3


class EKSManager:
    def __init__(self, region_name, access_key_id, secret_access_key, cluster_name):
        self.client = boto3.client('eks', region_name=region_name,
                                   aws_access_key_id=access_key_id,
                                   aws_secret_access_key=secret_access_key)
        self.cluster_name = cluster_name

    def update_nodegroup_scaling(self, nodegroup, min_size, max_size, desired_size):
        """更新EKS节点组的伸缩配置"""
        response = self.client.update_nodegroup_config(
            clusterName=self.cluster_name,
            nodegroupName=nodegroup,
            scalingConfig={
                'minSize': min_size,
                'maxSize': max_size,
                'desiredSize': desired_size
            }
        )
        # 检查操作是否成功
        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def get_nodegroup_desired_size(self, nodegroup_name):
        """获取指定节点组的期望节点数量"""
        response = self.client.describe_nodegroup(
            clusterName=self.cluster_name,
            nodegroupName=nodegroup_name
        )
        if 'nodegroup' in response:
            return response['nodegroup']['scalingConfig']['desiredSize']
        return None

    def list_nodegroups(self):
        """列出EKS集群中所有节点组的名称"""
        response = self.client.list_nodegroups(clusterName=self.cluster_name)
        if 'nodegroups' in response:
            return response['nodegroups']
        return []
