import openstack
import paramiko
import time

def get_vm_ips(conn, vm_name):
    server = conn.compute.find_server(vm_name)
    server = conn.compute.get_server(server.id)
    fixed_ip = None
    floating_ip = None

    for net in server.addresses.values():
        for addr in net:
            if addr['OS-EXT-IPS:type'] == 'floating':
                floating_ip = addr['addr']
            elif addr['OS-EXT-IPS:type'] == 'fixed':
                fixed_ip = addr['addr']

    return fixed_ip, floating_ip

def ssh_and_ping(host_ip, target_ips, username='cirros', password='gocubsgo'):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Connecting to {host_ip} via SSH...")
        ssh.connect(host_ip, username=username, password=password, timeout=10)
        print("Connected.")

        for ip in target_ips:
            print(f"Pinging {ip} from {host_ip}...")
            stdin, stdout, stderr = ssh.exec_command(f"ping -c 3 {ip}")
            time.sleep(1)
            output = stdout.read().decode()
            print(output)

    except Exception as e:
        print(f"SSH or Ping failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    conn = openstack.connect()

    # Get all VM IPs
    vm1_fixed, vm1_floating = get_vm_ips(conn, "vm1")
    vm2_fixed, _ = get_vm_ips(conn, "vm2")
    vm3_fixed, _ = get_vm_ips(conn, "vm3")

    print(f"VM1 floating IP: {vm1_floating}")
    print(f"VM2 fixed IP: {vm2_fixed}")
    print(f"VM3 fixed IP: {vm3_fixed}")

    # SSH into VM1 and ping VM2 and VM3
    ssh_and_ping(vm1_floating, [vm2_fixed, vm3_fixed])

