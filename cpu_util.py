#!/usr/bin/python3
from netmiko import ConnectHandler

def fetch_cpu(conn):
    command = "top -bn1 | grep 'CPU' | head -n1"
    output = conn.send_command(command)
    print(output.find("idle"))

def main():
    instance_ip = "172.24.4.197"
    username = "cirros"
    password = "roomtoor"
    device = {
        "device_type": "linux",
        "host": instance_ip,
        "username": username,
        "password": password
    }   
    conn = ConnectHandler(**device)
    fetch_cpu(conn)

if __name__ == "__main__":
    main()
