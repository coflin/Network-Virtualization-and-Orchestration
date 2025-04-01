import openstack

def create_vn(conn, network_name, subnet_name, router_name, subnet_cidr):
    # Create Network
    network = conn.network.create_network(name=network_name)
    print(f"Network '{network_name}' created.")

    # Create Subnet
    ntwk_sub = (subnet_cidr.split('/')[0]).split('.')[0:3]
    network_subnet = '.'.join(ntwk_sub) + '.1'
    print(network_subnet)
    subnet = conn.network.create_subnet(
        name=subnet_name,
        network_id=network.id,
        ip_version='4',
        cidr=subnet_cidr,
        gateway_ip=(network_subnet)
    )
    print(f"Subnet '{subnet_name}' created.")

    # Create Router
    router = conn.network.create_router(name=router_name, external_gateway_info={
        "network_id": conn.network.find_network('public').id
    })
    print(f"Router '{router_name}' created.")

    # Attach Subnet to Router
    conn.network.add_interface_to_router(router, subnet_id=subnet.id)
    print(f"Attached subnet '{subnet_name}' to router '{router_name}'.")


if __name__ == "__main__":
    conn = openstack.connect()

    create_vn(
        conn,
        network_name="vn1",
        subnet_name="vn1-subnet",
        router_name="vn1-router",
        subnet_cidr="10.10.1.0/24"
    )

    create_vn(
        conn,
        network_name="vn2",
        subnet_name="vn2-subnet",
        router_name="vn2-router",
        subnet_cidr="10.10.2.0/24"
    )
