#/usr/bin/python3

from ec2 import get_running_instances, stop_instance, launch_instances, print_instance_details
import boto3
from loguru import logger
from datetime import datetime, timedelta, UTC
import time

# 🔹 CPU Threshold for Scaling
CPU_THRESHOLD = 5.0  
CHECK_INTERVAL = 5  # Time interval (in seconds) to check CPU usage

# 🔹 AWS Clients
session = boto3.Session()
cloudwatch = session.client('cloudwatch')
sns = session.client('sns')

# 🔹 SNS Topic ARN (Replace with your SNS topic ARN)
SNS_TOPIC_ARN = "arn:aws:sns:us-west-1:771602930318:EC2-Launch-Alerts"

def send_sns_notification(instance_id, new_instance_ids):
    """Sends an SNS notification when CPU threshold is breached and new instances are launched."""
    subject = "🚨 High CPU Utilization: Instance Replaced"
    body = (
        f"Instance {instance_id} exceeded the CPU threshold ({CPU_THRESHOLD}%) and has been stopped.\n\n"
        f"New instance(s) launched:\n{', '.join(new_instance_ids)}\n\n"
        f"Time: {datetime.now(UTC)}"
    )

    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=subject,
        Message=body
    )
    logger.info(f"📧 SNS notification sent: {response['MessageId']}")

def get_cpu_utilization(instance_id):
    """Fetches CPU utilization from CloudWatch."""
    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(minutes=5)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average']
    )

    return response['Datapoints'][-1]['Average'] if response['Datapoints'] else 0.0

def monitor_instances():
    """Monitors instances and launches new ones if CPU threshold is exceeded."""
    while True:
        instances = get_running_instances()
        if len(instances) < 2:
            logger.warning("Not enough running instances. Waiting...")
            time.sleep(CHECK_INTERVAL)
            continue

        logger.info("Checking CPU utilization...")
        high_cpu_instances = []
        
        for instance in instances[:2]:  # Monitor only first two instances
            cpu_usage = get_cpu_utilization(instance.id)
            logger.info(f"Instance {instance.id}: CPU {cpu_usage:.2f}%")
            
            if cpu_usage >= CPU_THRESHOLD:
                high_cpu_instances.append(instance.id)

        # If high CPU instances are found, stop and replace them
        if high_cpu_instances:
            new_instance_ids = []
            for instance_id in high_cpu_instances:
                logger.warning(f"{instance_id} breached the CPU threshold. Stopping instance and launching a new one..")
                stop_instance(instance_id)

            new_instances = launch_instances(len(high_cpu_instances))
            new_instance_ids = [instance.id for instance in new_instances]
            print_instance_details(new_instances)

            # Send SNS Notification
            send_sns_notification(high_cpu_instances[0], new_instance_ids)

        logger.info("Waiting for next check...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_instances()
