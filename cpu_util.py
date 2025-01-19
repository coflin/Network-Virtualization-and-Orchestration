#!/usr/bin/python3
from netmiko import ConnectHandler
import re
import time
from sshInfo import sshInfo
from create_instance import create_cirros_instance
import openstack

# Global variables
instance_count = 1
MAX_INSTANCES = 5  # Maximum number of instances to create
CPU_THRESHOLD = 30  # CPU utilization threshold percentage

def fetch_cpu(conn, device):
    """
    Fetches CPU utilization from a device using SSH.
    """
    try:
        command = "top -bn1 | grep 'CPU' | head -n1"
        output = conn.send_command(command)

        match = re.search(r"(\d+%)\s+idle", output)
        if match:
            # Calculate CPU utilization from idle percentage
            cpu_util = 100 - int(match.group(1)[:-1])
            print(f"{device} CPU Utilization: {cpu_util}%")
            return cpu_util
        else:
            print(f"Error finding CPU utilization on {device}")
            return None
    except Exception as e:
        print(f"Error fetching CPU utilization for {device}: {e}")
        return None

def monitor_instances():
    """
    Monitors CPU utilization of instances and creates new instances if needed.
    """
    global instance_count
    conn = openstack.connect()
    credentials = sshInfo()

    while instance_count <= MAX_INSTANCES:
        for device in credentials:
            device_conn = {
                "device_type": credentials[device]["Device_Type"],
                "host": credentials[device]["IP"],
                "username": credentials[device]["Username"],
                "password": credentials[device]["Password"]
            }

            try:
                with ConnectHandler(**device_conn) as ssh_conn:
                    cpu_util = fetch_cpu(ssh_conn, device)

                    # Check if CPU utilization exceeds the threshold
                    if cpu_util is not None and cpu_util > CPU_THRESHOLD:
                        if instance_count < MAX_INSTANCES:
                            print(f"CPU utilization for {device} exceeds {CPU_THRESHOLD}%. Creating a new instance...")
                            create_cirros_instance(conn, instance_count)
                            instance_count += 1
                        elif instance_count == MAX_INSTANCES:
                            print(
                                "CPU utilization threshold breached. "
                                f"{MAX_INSTANCES} instances have already been created. "
                                "No additional instances will be spun up."
                            )
                            return  # Exit monitoring loop once max instances are reached
            except Exception as e:
                print(f"Error monitoring {device}: {e}")

        # Sleep before the next monitoring cycle
        time.sleep(1)

def main():
    """
    Main function to start monitoring.
    """
    print("Starting instance CPU utilization monitoring...")
    monitor_instances()

if __name__ == "__main__":
    main()
