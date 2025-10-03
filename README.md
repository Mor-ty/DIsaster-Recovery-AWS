<project>
  <title>Disaster Recovery for DynamoDB with AWS Backup and Lambda</title>

  <purpose>
    This project implements a disaster recovery mechanism for a DynamoDB table.
    It monitors real-time changes to the table and automatically restores previous states using AWS Backup's Point-in-Time Recovery (PITR).
    The goal is to ensure that deleted or modified data can be recovered within seconds of any unintended changes.
  </purpose>

  <resourcesUsed>
    <resource>DynamoDB Table (Primary Region)</resource>
    <resource>DynamoDB Streams (NEW_AND_OLD_IMAGES)</resource>
    <resource>AWS Backup Vault</resource>
    <resource>AWS Backup Plan (Scheduled and PITR enabled)</resource>
    <resource>Lambda Function: Change Monitor (triggered on DynamoDB Stream events)</resource>
    <resource>IAM Roles: 
      <role>Lambda execution role (with dynamodb:DescribeStream, GetRecords, StartRestoreJob)</role>
      <role>AWS Backup restore role (PassRole permissions)</role>
    </resource>
    <resource>CloudWatch Logs (to monitor Lambda execution and restore activity)</resource>
  </resourcesUsed>

  <planOfAction>
    <step>
      <description>Create DynamoDB table in primary region and optionally add items.</description>
    </step>
    <step>
      <description>Enable DynamoDB Streams with NEW_AND_OLD_IMAGES for the table.</description>
    </step>
    <step>
      <description>Create a backup vault in AWS Backup.</description>
    </step>
    <step>
      <description>Create a backup plan:
        <details>
          Scheduled backups every 12 hours
          Retain backups for 35 days
          Enable PITR
        </details>
      </description>
    </step>
    <step>
      <description>Create a Lambda function (Change Monitor) to monitor stream events:
        <details>
          Triggered on INSERT, MODIFY, REMOVE
          Calls StartRestoreJob to restore table from latest recovery point before change
        </details>
      </description>
    </step>
    <step>
      <description>Attach IAM roles and necessary permissions to Lambda and AWS Backup.</description>
    </step>
    <step>
      <description>Test by adding, modifying, and deleting items in DynamoDB table.</description>
    </step>
    <step>
      <description>Check CloudWatch logs and restored table to validate recovery process.</description>
    </step>
  </planOfAction>

  <commandsUsed>
    <command>
      <description>Create DynamoDB table</description>
      <bash>aws dynamodb create-table --table-name dynamo-demo --attribute-definitions AttributeName=LockId,AttributeType=S --key-schema AttributeName=LockId,KeyType=HASH --billing-mode PAY_PER_REQUEST --region us-west-1</bash>
    </command>
    <command>
      <description>Enable Streams</description>
      <bash>aws dynamodb update-table --table-name dynamo-demo --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES --region us-west-1</bash>
    </command>
    <command>
      <description>Create Backup Vault</description>
      <bash>aws backup create-backup-vault --backup-vault-name DynamoDRVault --region us-west-1</bash>
    </command>
    <command>
      <description>Create Backup Plan</description>
      <bash>aws backup create-backup-plan --backup-plan file://backup-plan.json --region us-west-1</bash>
    </command>
    <command>
      <description>Create Backup Selection for DynamoDB table</description>
      <bash>aws backup create-backup-selection --backup-plan-id <plan-id> --backup-selection file://backup-selection.json --region us-west-1</bash>
    </command>
    <command>
      <description>Deploy Lambda function (Change Monitor)</description>
      <bash>aws lambda create-function --function-name disaster-recovery-function --runtime python3.13 --role <lambda-role-arn> --handler recovery-lambda.lambda_handler --zip-file fileb://recovery-lambda.zip --region us-west-1</bash>
    </command>
    <command>
      <description>Attach DynamoDB stream as Lambda trigger</description>
      <bash>aws lambda create-event-source-mapping --function-name disaster-recovery-function --event-source-arn <stream-arn> --starting-position LATEST --region us-west-1</bash>
    </command>
    <command>
      <description>Test inserting an item</description>
      <bash>aws dynamodb put-item --table-name dynamo-demo --item '{"LockId": {"S": "101"}, "Name": {"S": "TestUser"}}' --region us-west-1</bash>
    </command>
    <command>
      <description>Test deleting an item</description>
      <bash>aws dynamodb delete-item --table-name dynamo-demo --key '{"LockId": {"S": "101"}}' --region us-west-1</bash>
    </command>
  </commandsUsed>

  <results>
    <result>
      Lambda triggers automatically on table changes
    </result>
    <result>
      CloudWatch logs display received events and restore job details
    </result>
    <result>
      DynamoDB table is restored to previous state based on PITR
    </result>
    <result>
      Backup plan ensures recovery points are available every 12 hours and retained for 35 days
    </result>
  </results>

</project>
