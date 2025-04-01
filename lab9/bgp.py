import docker
import os

GOBGP_CONTAINER_NAME = "gobgp-speaker"
GOBGP_IMAGE = "osrg/gobgp"
GOBGP_CONFIG_HOST_PATH = os.path.abspath("./configs/gobgp/gobgp.conf")
GOBGP_CONFIG_CONTAINER_PATH = "/gobgp/gobgp.conf"
BGP_NETWORK_NAME = "bgp-net"
GOBGP_CONTAINER_IP = "10.0.0.2"

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

def start_gobgp_container():
    client = docker.from_env()
    create_docker_network()

    print(f"Pulling GoBGP image {GOBGP_IMAGE}...")
    client.images.pull(GOBGP_IMAGE)

    try:
        existing = client.containers.get(GOBGP_CONTAINER_NAME)
        existing.stop()
        existing.remove()
        print("Old GoBGP container removed.")
    except docker.errors.NotFound:
        pass

    print("Starting new GoBGP BGP speaker container...")
    container = client.containers.run(
        image=GOBGP_IMAGE,
        name=GOBGP_CONTAINER_NAME,
        entrypoint="gobgpd",
        command=["-f", GOBGP_CONFIG_CONTAINER_PATH, "-l", "info"],
        detach=True,
        tty=True,
        stdin_open=True,
        volumes={
            GOBGP_CONFIG_HOST_PATH: {
                'bind': GOBGP_CONFIG_CONTAINER_PATH,
                'mode': 'ro'
            }
        },
        network=BGP_NETWORK_NAME,
        hostname="gobgp-speaker"
    )

    print(f"GoBGP container '{GOBGP_CONTAINER_NAME}' started with IP {GOBGP_CONTAINER_IP}.")
    return container

if __name__ == "__main__":
    if not os.path.isfile(GOBGP_CONFIG_HOST_PATH):
        print(f"GoBGP config not found at {GOBGP_CONFIG_HOST_PATH}. Please create it.")
    else:
        start_gobgp_container()

