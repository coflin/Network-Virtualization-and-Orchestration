import subprocess
import platform
from prettytable import PrettyTable
from termcolor import colored

# List of hostnames or IPs to ping
hosts = {
    "kubemaster": "192.168.56.74",
    "kubenode1": "192.168.56.221",
    "kubenode2": "192.168.56.135",
    "host-vm": "172.24.4.1"
}

# Detect ping count based on OS
param = "-n" if platform.system().lower() == "windows" else "-c"

# Create table
table = PrettyTable()
table.field_names = ["Host", "IP", "Ping Status"]

for name, ip in hosts.items():
    try:
        output = subprocess.check_output(["ping", param, "1", ip], stderr=subprocess.DEVNULL)
        status = colored("Success", "green")
    except subprocess.CalledProcessError:
        status = colored("Failed", "red")
    
    table.add_row([name, ip, status])

print(table)