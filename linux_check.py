# linux_check.py

import boto3
import time
import sys

def run_disk_check(instance_id):
    ssm = boto3.client('ssm')

    print(f"\n🛠 Sending disk inspection command to Linux instance: {instance_id}...\n")

    commands = [
        'echo "📊 Disk Usage Summary:"',
        'df -h',
        '',
        'echo "\\n📁 Top 10 Largest Files or Directories:"',
        'du -ahx / --max-depth=5 2>/dev/null | sort -hr | head -n 10',
        '',
        'echo "\\n📈 Recently Modified Files (last 24h):"',
        'find / -type f -mtime -1 -printf "%TY-%Tm-%Td %TT %s %p\\n" 2>/dev/null | sort -hr | head -n 10'
    ]

    try:
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': commands},
            CloudWatchOutputConfig={'CloudWatchOutputEnabled': False}
        )

        command_id = response['Command']['CommandId']
        print(f"✅ Command sent. Waiting for results... (Command ID: {command_id})")

        for _ in range(20):
            time.sleep(3)
            output = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            if output['Status'] in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
                break

        if output['Status'] == 'Success':
            print("\n📦 Disk Inspection Results:\n")
            print(output['StandardOutputContent'])
        else:
            print(f"\n⚠️ Command failed or incomplete: {output['Status']}")
            print("Error Output:\n", output['StandardErrorContent'])

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
