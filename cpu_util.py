#!/usr/bin/python3
from netmiko import ConnectHandler
import re
from sshInfo import sshInfo

def fetch_cpu(conn, device):
    command = "top -bn1 | grep 'CPU' | head -n1"
    output = conn.send_command(command)

    match = re.search(r"(\d+%)\s+idle", output)
    if match:
        cpu_util = 100 - int(match.group(1)[:-1])
        print(f" {device} CPU Utilization: {cpu_util}%") 
    else:
        print("Error finding CPU utilization")

def main():
    credentials = sshInfo()
    for device in credentials:
        device_conn = {
            "device_type":  credentials[device]["Device_Type"],
            "host": credentials[device]["IP"],
            "username": credentials[device]["Username"],
            "password": credentials[device]["Password"]
        }
        conn = ConnectHandler(**device_conn)
        fetch_cpu(conn,device)

    # instance_ip = "172.24.4.197"
    # username = "cirros"
    # password = "roomtoor"
    # device = {
    #     "device_type": "linux",
    #     "host": instance_ip,
    #     "username": username,
    #     "password": password
    # }   
    # conn = ConnectHandler(**device)
    # fetch_cpu(conn)

if __name__ == "__main__":
    main()
