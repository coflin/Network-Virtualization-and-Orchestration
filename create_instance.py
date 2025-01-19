import openstack

# Constants for OpenStack resources
INSTANCE_NAME_PREFIX = "cirros-auto"
FLAVOR_NAME = "m1.tiny"
IMAGE_NAME = "cirros-0.6.3-x86_64-disk"
NETWORK_NAME = "internal-network-1"
SECURITY_GROUP = "261ba6d0-17ad-4b72-9150-b2ea32108dff"

def create_cirros_instance(conn, instance_count):
    """
    Creates a new Cirros instance in OpenStack and adds it to the default security group.
    """
    instance_name = f"{INSTANCE_NAME_PREFIX}-{instance_count}"
    print(f"Creating new instance: {instance_name}")

    try:
        # Find resources
        image = conn.compute.find_image(IMAGE_NAME)
        flavor = conn.compute.find_flavor(FLAVOR_NAME)
        network = conn.network.find_network(NETWORK_NAME)
        security_group = conn.network.find_security_group(SECURITY_GROUP)

        if not image or not flavor or not network or not security_group:
            raise Exception("One or more resources (image, flavor, network, security group) not found.")

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
    except Exception as e:
        print(f"Error creating instance: {e}")

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
