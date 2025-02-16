#/usr/bin/python3

import argparse
from ec2 import launch_instances, print_instance_details

def main():
    """Parses user input and launches EC2 instances based on arguments."""
    parser = argparse.ArgumentParser(description="Launch EC2 instances with custom settings.")

    # Argument for number of instances
    parser.add_argument(
        "--count",
        type=int,
        default=2,
        help="Number of EC2 instances to launch (default: 2)"
    )

    # Argument for instance name prefix
    parser.add_argument(
        "--name",
        type=str,
        default="NVO Auto-generated",
        help="Base name for EC2 instances (default: 'NVO Auto-generated')"
    )

    args = parser.parse_args()

    # Launch instances with user-defined count
    instances = launch_instances(args.count)

    # Rename instances with sequential numbering
    for i, instance in enumerate(instances, start=1):
        instance.create_tags(Tags=[{'Key': 'Name', 'Value': f"{args.name} {i}"}])

    print_instance_details(instances)  # Display instance details

if __name__ == "__main__":
    main()
