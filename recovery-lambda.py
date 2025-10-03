import boto3
import os
import datetime

backup = boto3.client('backup')
ddb = boto3.client('dynamodb')

BACKUP_PLAN_ID = os.environ.get("BACKUP_PLAN_ID")  # pass via env
VAULT_NAME = os.environ.get("VAULT_NAME")     # pass via env
TABLE_NAME = os.environ.get("TABLE_NAME", "dynamo-demo") 

def lambda_handler(event, context):
    print("Received event:", event)

    for record in event['Records']:
        event_name = record['eventName']   # INSERT, MODIFY, REMOVE
        old_image = record.get('dynamodb', {}).get('OldImage', {})
        new_image = record.get('dynamodb', {}).get('NewImage', {})

        if event_name == "REMOVE":  
            # If deletion occurs, trigger restore
            print("Detected deletion:", old_image)

            # Step 1: List latest recovery points
            response = backup.list_recovery_points_by_backup_vault(
                BackupVaultName=VAULT_NAME,
                ByResourceType="DynamoDB"
            )

            if not response['RecoveryPoints']:
                print("No recovery points found. Skipping restore.")
                return {"status": "no backups found"}  # stop Lambda gracefully

            latest = sorted(
                response['RecoveryPoints'],
                key=lambda x: x['CreationDate'],
                reverse=True
            )[0]
            recovery_point_arn = latest['RecoveryPointArn']
            print("Latest recovery point:", latest['RecoveryPointArn'])

            # Step 2: Start restore job
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            target_table_name = f"{TABLE_NAME}-restored-{timestamp}"
            restore = backup.start_restore_job(
                RecoveryPointArn=recovery_point_arn,
                IamRoleArn="arn:aws:iam::649418801828:role/AWS-Backup-Rrestore-Role",
                ResourceType="DynamoDB",
                Metadata={
                    "TableName": TABLE_NAME,
                    "TargetTableName": target_table_name
                }
            )
            
            print("Restore triggered:", restore['RestoreJobId'])

    return {"status": "success"}
