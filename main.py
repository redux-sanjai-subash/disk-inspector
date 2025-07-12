# main.py

import boto3
import sys
from tabulate import tabulate
from linux_check import run_disk_check  # Windows support can be added later

def get_ssm_enabled_instances():
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    instances = []
    instance_refs = []

    reservations = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])['Reservations']
    
    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), "(No Name)")
            
            try:
                ssm_info = ssm.describe_instance_information(
                    Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
                )
                if ssm_info['InstanceInformationList']:
                    os_type = ssm_info['InstanceInformationList'][0]['PlatformName']
                    volumes = ", ".join([
                        bdm['Ebs']['VolumeId']
                        for bdm in instance.get('BlockDeviceMappings', [])
                        if 'Ebs' in bdm
                    ])
                    instances.append([
                        len(instances) + 1, name, instance_id, os_type, volumes
                    ])
                    instance_refs.append({
                        "id": instance_id,
                        "name": name,
                        "os": os_type
                    })
            except:
                continue

    return instances, instance_refs

if __name__ == "__main__":
    print("🔍 Fetching SSM-enabled EC2 instances...\n")

    table, refs = get_ssm_enabled_instances()

    if not table:
        print("❌ No eligible instances found.")
        sys.exit(0)

    print(tabulate(table, headers=["#", "Instance Name", "Instance ID", "OS Type", "Volume IDs"], tablefmt="grid"))

    try:
        choice = int(input("\n💡 Enter the instance number to inspect disk usage: "))
        selected = refs[choice - 1]
        print(f"\n➡️ Selected: {selected['name']} ({selected['id']})")
        print(f"📦 OS Detected: {selected['os']}")

        # ✅ Check for Linux or Ubuntu
        if 'linux' in selected['os'].lower() or 'ubuntu' in selected['os'].lower():
            run_disk_check(selected['id'])
        else:
            print("⚠️ Windows check not implemented yet.")
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        sys.exit(1)
