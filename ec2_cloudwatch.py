#/usr/bin/python3

import boto3
from loguru import logger
from datetime import datetime, timedelta, UTC
from tabulate import tabulate  # Import tabulate for table formatting

# 🔹 Use default AWS credentials from aws configure
session = boto3.Session()

# 🔹 Create CloudWatch and EC2 clients
cloudwatch = session.client('cloudwatch')
ec2 = session.client('ec2')

# 🔹 Get the first running EC2 instance
instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

if not instances['Reservations']:
    logger.error("No running EC2 instances found.")
    exit()

instance_details = instances['Reservations'][0]['Instances'][0]
instance_id = instance_details['InstanceId']

# 🔹 Fetch Instance Name from Tags
instance_name = "No Name"
if 'Tags' in instance_details:
    for tag in instance_details['Tags']:
        if tag['Key'] == 'Name':
            instance_name = tag['Value']
            break

logger.info(f"Fetching CloudWatch metrics for Instance: {instance_name} (ID: {instance_id})")

# 🔹 Define the time range (last 30 minutes) using UTC-aware datetime
end_time = datetime.now(UTC)
start_time = end_time - timedelta(minutes=30)
formatted_start = start_time.strftime('%Y-%m-%d %H:%M:%S UTC')
formatted_end = end_time.strftime('%Y-%m-%d %H:%M:%S UTC')

# 🔹 Function to fetch CloudWatch metrics with multiple statistics
def get_metric_stats(metric_name, namespace, statistics):
    response = cloudwatch.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,  # Fetch data every 5 minutes
        Statistics=statistics
    )

    if response['Datapoints']:
        latest_data = response['Datapoints'][-1]  # Get the latest datapoint
        return {stat: latest_data.get(stat, "No Data") for stat in statistics}
    else:
        return {stat: "No Data" for stat in statistics}

# 🔹 Fetch required metrics
status_check = "Running"
cpu_stats = get_metric_stats("CPUUtilization", "AWS/EC2", ["Minimum", "Maximum", "Average"])
network_in = get_metric_stats("NetworkIn", "AWS/EC2", ["Sum"])["Sum"]
network_out = get_metric_stats("NetworkOut", "AWS/EC2", ["Sum"])["Sum"]

# 🔹 Prepare Data for Table Output
table_data = [
    ["Instance Name", instance_name],
    ["Instance ID", instance_id],
    ["Time Frame", f"{formatted_start} → {formatted_end}"],
    ["Status Check", status_check],
    ["CPU Min (%)", f"{cpu_stats['Minimum']:.2f}%" if isinstance(cpu_stats["Minimum"], (int, float)) else cpu_stats["Minimum"]],
    ["CPU Max (%)", f"{cpu_stats['Maximum']:.2f}%" if isinstance(cpu_stats["Maximum"], (int, float)) else cpu_stats["Maximum"]],
    ["CPU Average (%)", f"{cpu_stats['Average']:.2f}%" if isinstance(cpu_stats["Average"], (int, float)) else cpu_stats["Average"]],
    ["Network In (Bytes)", f"{network_in:.2f}" if isinstance(network_in, (int, float)) else network_in],
    ["Network Out (Bytes)", f"{network_out:.2f}" if isinstance(network_out, (int, float)) else network_out]
]

# 🔹 Print and log results in table format
table_output = tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid")
logger.success(f"\n{table_output}\n")
