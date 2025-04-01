import docker
import os

FRR_CONTAINER_NAME = "frr-router"
FRR_IMAGE = "frrouting/frr:latest"
HOST_CONFIG_DIR = os.path.abspath("./configs/frr")
CONTAINER_CONFIG_DIR = "/etc/frr"
BGP_NETWORK_NAME = "bgp-net"
FRR_CONTAINER_IP = "10.0.0.1"

vtysh_commands = [
    "configure terminal",
    "router bgp 65001",
    "bgp router-id 1.1.1.1",
    "neighbor 10.0.0.2 remote-as 65002",
    "network 10.0.0.0/24",
    "end",
    "write memory"
]

def start_daemons(container):
    print("\n>> Starting FRR daemons (zebra & bgpd)...")
    container.exec_run("rm -f /var/run/frr/*.pid /var/run/frr/zserv.api")
    container.exec_run("/usr/lib/frr/zebra -d")
    container.exec_run("/usr/lib/frr/bgpd -d")

def run_vtysh_commands(container):
    print("\n>> Configuring FRR via vtysh...")
    full_command = "vtysh"
    for cmd in vtysh_commands:
        full_command += f" -c \"{cmd}\""

    print(f"$ {full_command}")
    exit_code, output = container.exec_run(full_command, demux=True)
    out, err = output
    if out:
        print(out.decode())
    if err:
        print("[stderr]", err.decode())

    print("\n>> BGP Summary:")
    exit_code, output = container.exec_run("vtysh -c 'show bgp summary'", demux=True)
    out, err = output
    if out:
        print(out.decode())
    if err:
        print("[stderr]", err.decode())

def create_docker_network():
    client = docker.from_env()
    try:
        client.networks.get(BGP_NETWORK_NAME)
        print(f"Docker network '{BGP_NETWORK_NAME}' already exists.")
    except docker.errors.NotFound:
        print(f"Creating Docker network '{BGP_NETWORK_NAME}'...")
        client.networks.create(
            BGP_NETWORK_NAME,
            driver="bridge",
            ipam=docker.types.IPAMConfig(
                pool_configs=[
                    docker.types.IPAMPool(
                        subnet="10.0.0.0/24",
                        gateway="10.0.0.254"
                    )
                ]
            )
        )

def start_frr_container():
    client = docker.from_env()
    create_docker_network()

    print(f"Pulling FRR image {FRR_IMAGE}...")
    client.images.pull(FRR_IMAGE)

    try:
        existing = client.containers.get(FRR_CONTAINER_NAME)
        existing.stop()
        existing.remove()
        print("Old FRR container removed.")
    except docker.errors.NotFound:
        pass

    print("Starting new FRR container...")
    networking_config = client.api.create_networking_config({
        BGP_NETWORK_NAME: client.api.create_endpoint_config(ipv4_address=FRR_CONTAINER_IP)
    })

    host_config = client.api.create_host_config(
        privileged=True,
        binds={
            HOST_CONFIG_DIR: {
                'bind': CONTAINER_CONFIG_DIR,
                'mode': 'rw'
            }
        }
    )

    container = client.api.create_container(
        image=FRR_IMAGE,
        name=FRR_CONTAINER_NAME,
        host_config=host_config,
        networking_config=networking_config,
        tty=True,
        stdin_open=True
    )
    client.api.start(container=container.get('Id'))
    print(f"FRR container '{FRR_CONTAINER_NAME}' started with IP {FRR_CONTAINER_IP}.")
    return client.containers.get(container.get('Id'))

if __name__ == "__main__":
    if not os.path.isdir(HOST_CONFIG_DIR):
        print(f"FRR config dir '{HOST_CONFIG_DIR}' not found! Please create it with frr.conf + daemons file.")
    else:
        container = start_frr_container()
        start_daemons(container)
        run_vtysh_commands(container)
