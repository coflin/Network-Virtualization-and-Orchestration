import openstack

# Constants for OpenStack resources
INSTANCE_NAME_PREFIX = "cirros-auto"
FLAVOR_NAME = "m1.tiny"
IMAGE_NAME = "cirros-0.6.3-x86_64-disk"
NETWORK_NAME = "internal-network-1"
SECURITY_GROUP = "default"  # Name of the security group
PUBLIC_NETWORK = "public"   # Name of the public network for floating IPs

def create_cirros_instance(conn, instance_count):
    """
    Creates a new Cirros instance in OpenStack, adds it to the default security group,
    and associates a floating IP from the public network.
    """
    instance_name = f"{INSTANCE_NAME_PREFIX}-{instance_count}"
    print(f"Creating new instance: {instance_name}")

    try:
        # Find resources
        image = conn.compute.find_image(IMAGE_NAME)
        flavor = conn.compute.find_flavor(FLAVOR_NAME)
        network = conn.network.find_network(NETWORK_NAME)
        security_group = conn.network.find_security_group(SECURITY_GROUP)
        public_network = conn.network.find_network(PUBLIC_NETWORK)

        if not image or not flavor or not network or not security_group or not public_network:
            raise Exception("One or more resources (image, flavor, network, security group, public network) not found.")

        # Launch the instance with the default security group
        instance = conn.compute.create_server(
            name=instance_name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            security_groups=[{"name": security_group.name}],
        )

        # Wait for the instance to become active
        conn.compute.wait_for_server(instance)
        print(f"Instance {instance_name} created successfully!")

        # Associate a floating IP
        print("Allocating and associating a floating IP...")
        floating_ip = allocate_and_associate_floating_ip(conn, instance, public_network.id)
        print(f"Floating IP {floating_ip.floating_ip_address} associated with instance {instance_name}.")

    except Exception as e:
        print(f"Error creating instance: {e}")

def allocate_and_associate_floating_ip(conn, instance, public_network_id):
    """
    Allocates a floating IP from the public network and associates it with the instance.
    """
    # Allocate a new floating IP from the public network
    floating_ip = conn.network.create_ip(floating_network_id=public_network_id)

    # Get the instance's first port
    ports = list(conn.network.ports(device_id=instance.id))
    if not ports:
        raise Exception(f"No ports found for instance {instance.name}.")

    # Associate the floating IP with the first port
    conn.network.update_ip(floating_ip, port_id=ports[0].id)
    return floating_ip

def main():
    """
    Main function to create instances.
    """
    # Connect to OpenStack
    try:
        conn = openstack.connect()
    except Exception as e:
        print(f"Failed to connect to OpenStack: {e}")
        return

    # Create a new Cirros instance
    instance_count = 1
    print("Spinning up a new Cirros instance...")
    create_cirros_instance(conn, instance_count)

if __name__ == "__main__":
    main()
