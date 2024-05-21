from dotenv import load_dotenv
import os
import json
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
DOCDB_CLUSTER_NAME = os.getenv('DOCDB_CLUSTER_NAME')
RDS_CLUSTER_NAME = os.getenv('RDS_CLUSTER_NAME')
EKS_CLUSTER_NAME = os.getenv('EKS_CLUSTER_NAME')
EKS_NODE_GROUPS = json.loads(os.getenv('EKS_NODE_GROUPS'))