#/usr/bin/python3

import boto3
from loguru import logger
import time
import itertools
import sys

# Create EC2 resource
ec2 = boto3.resource('ec2')

def launch_instances(count=2):
    """Launches 'count' EC2 instances."""
    instances = ec2.create_instances(
        ImageId='ami-07d2649d67dbe8900',  # Replace with your AMI ID
        MinCount=count,
        MaxCount=count,
        InstanceType='t2.micro',
        KeyName='mac-new',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'NVO Auto-Generated'}]
            }
        ]
    )

    # Wait for instances to be running
    for i, instance in enumerate(instances, start=1):
        instance.wait_until_running()
        instance.reload()  # Refresh instance details
        instance.create_tags(Tags=[{'Key': 'Name', 'Value': f'NVO Auto-generated {i}'}])

    logger.success(f"Launched {count} instances.")
    return instances

def stop_instance(instance_id):
    """Stops an EC2 instance given its instance ID."""
    ec2.instances.filter(InstanceIds=[instance_id]).stop()
    logger.warning(f"Stopped instance: {instance_id}")

def get_running_instances():
    """Fetches all running EC2 instances."""
    return list(ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]))  

def print_instance_details(instances):
    """Prints details of given EC2 instances."""
    for instance in instances:
        instance_name = next((tag['Value'] for tag in instance.tags if tag['Key'] == 'Name'), "No Name") if instance.tags else "No Name"
        logger.success(
            f"Instance ID: {instance.id}\n"
            f"Name: {instance_name}\n"
            f"Type: {instance.instance_type}\n"
            f"State: {instance.state['Name']}\n"
            f"Private IP: {instance.private_ip_address}\n"
            f"Public IP: {instance.public_ip_address}\n"
            f"Launch Time: {instance.launch_time}\n"
            f"{'-'*50}"
        )

def animated_countdown(seconds, message="Stopping instance in"):
    """Displays an animated countdown before stopping an instance."""
    dots = itertools.cycle(['.  ', '.. ', '...'])
    while seconds >= 1:
        sys.stdout.write(f"\rDEBUG    | {message} {seconds}s{next(dots)}")
        sys.stdout.flush()
        seconds -= 1
        time.sleep(1)
    sys.stdout.write("\n")  # Move to a new line after countdown finishes

def main():
    """Main function to launch instances and stop one instance."""
    instances = launch_instances()

    print_instance_details(instances)

    # Countdown before stopping one instance
    animated_countdown(10)

    # Stop the first instance
    stop_instance(instances[0].id)

    # Fetch and print remaining running instances
    running_instances = get_running_instances()
    logger.info("Fetching all running EC2 instance details...\n")
    print_instance_details(running_instances)

if __name__ == "__main__":
    main()
