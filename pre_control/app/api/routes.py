from . import api_blueprint
from flask import jsonify
from app.utils.aws_eks import *
from app.utils.aws_midd import *
from app.config.settings import *

docdb_manager = CloudDatabaseManager('docdb', AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
rds_manager = CloudDatabaseManager('rds', AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
eks_manager = EKSManager(AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, EKS_CLUSTER_NAME)


@api_blueprint.route('/pre/start', methods=['POST'])
def start_pre():
    docdb_manager.start_cluster(DOCDB_CLUSTER_NAME)
    rds_manager.start_cluster(RDS_CLUSTER_NAME)

    for pool in EKS_NODE_GROUPS:
        node_num = EKS_NODE_GROUPS.get(pool)
        eks_manager.update_nodegroup_scaling(pool, node_num, node_num, node_num)

    return jsonify({"message": "Start Pre"}), 200


@api_blueprint.route('/pre/stop', methods=['POST'])
def stop_pre():
    docdb_manager.stop_cluster(DOCDB_CLUSTER_NAME)
    rds_manager.stop_cluster(RDS_CLUSTER_NAME)

    nodegroups = eks_manager.list_nodegroups()
    for nodegroup in nodegroups:
        eks_manager.update_nodegroup_scaling(nodegroup, 0, 1, 0)

    return jsonify({"message": "Stop Pre Successful"}), 200


@api_blueprint.route('/pre/status')
def status_pre():
    docdb_status = docdb_manager.get_cluster_status(DOCDB_CLUSTER_NAME)
    rds_status = rds_manager.get_cluster_status(RDS_CLUSTER_NAME)

    # 列出所有节点组
    nodegroups = eks_manager.list_nodegroups()

    node_info = {}
    # 获取并打印指定节点组的期望节点数量
    for nodegroup_name in nodegroups:
        desired_size = eks_manager.get_nodegroup_desired_size(nodegroup_name)
        node_info[nodegroup_name] = desired_size

    return jsonify({"env_name": "Pre",
                    "dbinfo": {"docdb_status": docdb_status, "rds_status": rds_status},
                    "eks_node": node_info}), 200
