import openstack

def create_security_group(conn, sg_name):
    # Check if the security group already exists
    security_group = conn.network.find_security_group(sg_name)
    if not security_group:
        security_group = conn.network.create_security_group(name=sg_name)
        print(f"Security Group '{sg_name}' created.")
    else:
        print(f"Security Group '{sg_name}' already exists.")

    return security_group


def add_security_group_rules(conn, sg_id):
    # Allow all inbound ICMP traffic (Ping)
    conn.network.create_security_group_rule(
        security_group_id=sg_id,
        protocol='icmp',
        direction='ingress'
    )

    # Allow all inbound TCP traffic (for now)
    conn.network.create_security_group_rule(
        security_group_id=sg_id,
        protocol='tcp',
        port_range_min=1,
        port_range_max=65535,
        direction='ingress'
    )

    # Allow all traffic between VMs (intra-VN and inter-VN)
    conn.network.create_security_group_rule(
        security_group_id=sg_id,
        protocol=None,  # None means all protocols
        direction='ingress'
    )


def apply_security_group_to_vm(conn, vm_name, sg_name):
    server = conn.compute.find_server(vm_name)
    if not server:
        print(f"VM '{vm_name}' not found.")
        return

    security_group = conn.network.find_security_group(sg_name)
    if not security_group:
        print(f"Security Group '{sg_name}' not found.")
        return

    conn.compute.add_security_group_to_server(server, security_group)
    print(f"Applied Security Group '{sg_name}' to VM '{vm_name}'.")


if __name__ == "__main__":
    conn = openstack.connect()

    sg = create_security_group(conn, sg_name="all_access")
    add_security_group_rules(conn, sg.id)

    # Apply the security group to all VMs
    apply_security_group_to_vm(conn, "vm1", "all_access")
    apply_security_group_to_vm(conn, "vm2", "all_access")
    apply_security_group_to_vm(conn, "vm3", "all_access")
