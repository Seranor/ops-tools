import boto3
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudDatabaseManager:
    def __init__(self, service_name, region_name, access_key_id, secret_access_key):
        self.client = boto3.client(service_name, region_name=region_name,
                                   aws_access_key_id=access_key_id,
                                   aws_secret_access_key=secret_access_key
                                   )
        self.service_name = service_name

    def start_cluster(self, cluster_identifier):
        try:
            response = self.client.start_db_cluster(DBClusterIdentifier=cluster_identifier)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.info(f"Successfully started {self.service_name} cluster {cluster_identifier}.")
            else:
                logger.error(f"Failed to start {self.service_name} cluster {cluster_identifier}.")
        except Exception as e:
            logger.error(f"Exception occurred while starting {self.service_name} cluster {cluster_identifier}: {e}")

    def stop_cluster(self, cluster_identifier):
        try:
            response = self.client.stop_db_cluster(DBClusterIdentifier=cluster_identifier)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                logger.info(f"Successfully stopped {self.service_name} cluster {cluster_identifier}.")
            else:
                logger.error(f"Failed to stop {self.service_name} cluster {cluster_identifier}.")
        except Exception as e:
            logger.error(f"Exception occurred while stopping {self.service_name} cluster {cluster_identifier}: {e}")

    def get_cluster_status(self, cluster_identifier):
        try:
            response = self.client.describe_db_clusters(DBClusterIdentifier=cluster_identifier)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                cluster_status = response['DBClusters'][0]['Status']
                logger.info(f"{self.service_name} cluster {cluster_identifier} status is {cluster_status}.")
                return cluster_status
            else:
                logger.error(f"Failed to get status for {self.service_name} cluster {cluster_identifier}.")
        except Exception as e:
            logger.error(
                f"Exception occurred while getting status for {self.service_name} cluster {cluster_identifier}: {e}")
