#!/usr/bin/python3
from netmiko import ConnectHandler

def fetch_cpu():
    pass

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
    print(conn)

if __name__ == "__main__":
    main()
