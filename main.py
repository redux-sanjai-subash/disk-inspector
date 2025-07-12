# main.py

from common import get_ssm_managed_instances
from tabulate import tabulate
import sys

if __name__ == "__main__":
    print("🔍 Fetching EC2 instances with SSM enabled...\n")

    table, all_instances = get_ssm_managed_instances()

    if not table:
        print("❌ No SSM-enabled instances found.")
        sys.exit(0)

    print(tabulate(table, headers=["#", "Instance Name", "Instance ID", "OS Type", "Volume IDs"], tablefmt="grid"))

    try:
        choice = int(input("\n💡 Enter the instance number to inspect disk usage: "))
        selected = all_instances[choice - 1]
        print(f"\n➡️ Selected: {selected['name'] or '(No Name)'} ({selected['id']})")
        print(f"📦 OS Detected: {selected['os']}")
        print("🔗 Ready to run disk inspection (next step will trigger sub-script)...")
        # Next: import and call linux_check.run(selected) or windows_check.run(selected)
    except (ValueError, IndexError):
        print("❌ Invalid selection.")
        sys.exit(1)
