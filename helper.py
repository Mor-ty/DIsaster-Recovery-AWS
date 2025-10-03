import boto3

backup = boto3.client("backup")

def get_backup_plans_and_vaults():
    # List Backup Plans
    plans = backup.list_backup_plans()
    print("🔹 Backup Plans:")
    for p in plans["BackupPlansList"]:
        print(f"Name: {p['BackupPlanName']}, ID: {p['BackupPlanId']}")

    # List Backup Vaults
    vaults = backup.list_backup_vaults()
    print("\n🔹 Backup Vaults:")
    for v in vaults["BackupVaultList"]:
        print(f"Name: {v['BackupVaultName']}, ARN: {v['BackupVaultArn']}")

if __name__ == "__main__":
    get_backup_plans_and_vaults()
