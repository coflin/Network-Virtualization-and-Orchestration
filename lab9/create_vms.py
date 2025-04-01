import openstack

def create_vm(conn, vm_name, network_name, image_name, flavor_name):
    # Find the network to attach
    network = conn.network.find_network(network_name)

    # Find the image to use
    image = conn.compute.find_image(image_name)

    # Find the flavor to use
    flavor = conn.compute.find_flavor(flavor_name)

    # Create VM instance
    server = conn.compute.create_server(
        name=vm_name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}]
    )

    # Wait for the VM to be active
    server = conn.compute.wait_for_server(server)
    print(f"VM '{vm_name}' created and is now ACTIVE.")


if __name__ == "__main__":
    conn = openstack.connect()

    # Example usage - Single Tenant (Same VN)
    create_vm(
        conn,
        vm_name="vm1",
        network_name="vn1",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.small"
    )

    create_vm(
        conn,
        vm_name="vm2",
        network_name="vn1",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.small"
    )

    # Example usage - Multi-Tenant (Different VNs)
    create_vm(
        conn,
        vm_name="vm3",
        network_name="vn2",
        image_name="cirros-0.6.3-x86_64-disk",
        flavor_name="m1.small"
    )
