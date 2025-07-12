# common.py

import boto3
import botocore

def get_ssm_managed_instances():
    ec2 = boto3.client('ec2')
    ssm = boto3.client('ssm')

    instance_list = []
    instance_lookup = []

    try:
        # Get all running EC2 instances
        reservations = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )['Reservations']

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
                        instance_list.append([
                            len(instance_list) + 1,
                            name,
                            instance_id,
                            os_type,
                            volumes
                        ])
                        instance_lookup.append({
                            "id": instance_id,
                            "name": name,
                            "os": os_type
                        })
                except botocore.exceptions.ClientError:
                    continue

    except botocore.exceptions.ClientError as e:
        print(f"[ERROR] Failed to retrieve instance info: {e}")

    return instance_list, instance_lookup
