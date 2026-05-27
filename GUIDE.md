# AWS Disaster Recovery for DynamoDB - Interview Preparation Guide

## 🎯 Project Overview

**Project Name:** AWS Disaster Recovery for DynamoDB  
**Primary Purpose:** Automated disaster recovery mechanism for DynamoDB tables using AWS Backup, Lambda, and Point-in-Time Recovery (PITR)  
**Core Objective:** Ensure deleted or modified data can be restored to previous state within seconds of unintended changes  

### Business Motive

This project addresses critical data protection requirements:

- **Data Loss Prevention:** Accidental deletions or malicious modifications can be immediately recovered
- **Compliance Requirements:** Meets RPO (Recovery Point Objective) and RTO (Recovery Time Objective) standards
- **High Availability:** Ensures business continuity during data corruption incidents
- **Automated Recovery:** Eliminates manual intervention in disaster scenarios
- **Audit Trail:** Maintains recovery history for compliance and forensic analysis

### Problem Statement

Organizations face significant risks from:
- Human error (accidental deletions, incorrect updates)
- Malicious insider attacks
- Application bugs causing data corruption
- Ransomware attacks targeting databases

Traditional backup solutions have limitations:
- Manual restore processes are slow and error-prone
- Point-in-time recovery requires manual intervention
- No automated monitoring of data changes
- High RTO (Recovery Time Objective) impacts business continuity

---

## 📁 Code Structure & Architecture

```
DIsaster-Recovery-AWS/
├── README.md                          # Project documentation
├── helper.py                          # Backup vault/plan listing utility
├── recovery-lambda.py                 # Main Lambda function for DR
├── recovery-lambda.zip                # Deployed Lambda package
├── backup-plan.json                   # Backup plan configuration
├── backup-selection.json              # Resource selection configuration
└── Disaster-Recovery-AWS/             # Architecture diagrams and screenshots
    ├── Disaster_recovery_architecture_diagram.jpg
    ├── lambda-architecture.png
    ├── Roles.jpg
    ├── aws-bavkup-inline-policy-02.png
    ├── backup-plan-with-vault.png
    ├── cli-tail-logs-dbstream.png
    ├── lambda-role-inline-policy.png
    ├── lambda-role-policies-02.png
    ├── restore-job-success.png
    ├── restore-job-triggered.png
    └── restored-database-with-timestamp.png
```

### File Breakdown

#### **recovery-lambda.py** - Core Disaster Recovery Logic (58 lines)
**Purpose:** Lambda function triggered by DynamoDB Streams to automatically restore deleted data

**Key Components:**
- **Environment Variables:** BACKUP_PLAN_ID, VAULT_NAME, TABLE_NAME
- **Event Processing:** Handles INSERT, MODIFY, REMOVE events from DynamoDB Streams
- **Restore Logic:** Identifies latest recovery point and triggers restore job
- **Timestamp Naming:** Creates restored tables with unique timestamps

**Critical Functions:**
```python
def lambda_handler(event, context):
    # Process DynamoDB Stream events
    # Detect DELETE operations
    # Find latest recovery point
    # Trigger AWS Backup restore job
```

**Event Flow:**
1. Receives event from DynamoDB Streams
2. Checks if event is REMOVE (deletion)
3. Queries AWS Backup for latest recovery point
4. Initiates restore job with timestamped table name
5. Returns success status

#### **helper.py** - Administrative Utility (20 lines)
**Purpose:** List backup plans and vaults for monitoring and validation

**Functions:**
- `get_backup_plans_and_vaults()` - Retrieves and displays backup configuration

**Use Cases:**
- Verify backup plan creation
- Monitor vault status
- Troubleshoot backup issues

#### **backup-plan.json** - Backup Configuration (16 lines)
**Purpose:** Defines backup schedule and retention policy

**Configuration Details:**
- **Backup Plan Name:** DynamoDB-DR-Plan
- **Schedule:** Every 12 hours (cron expression)
- **Retention:** 35 days
- **Backup Window:** 60 minutes start window, 120 minutes completion window
- **Target Vault:** DynamoDB-DR-Vault

#### **backup-selection.json** - Resource Selection (6 lines)
**Purpose:** Specifies which DynamoDB tables to backup

**Configuration:**
- **Selection Name:** DynamoDB-Table-Selection
- **Target Resource:** Specific DynamoDB table ARN
- **IAM Role:** AWS Backup restore role

---

## ☁️ AWS Services Utilized

### 1. **DynamoDB (Primary Database)**
**Role:** Source database requiring protection

**Features Used:**
- **DynamoDB Streams:** Captures item-level changes in real-time
- **Stream View Type:** NEW_AND_OLD_IMAGES (captures both before and after state)
- **Change Data Capture:** Enables event-driven architecture

**API Methods:**
- Stream configuration via AWS Console or CLI
- Automatic event generation for INSERT, MODIFY, REMOVE operations

### 2. **DynamoDB Streams**
**Role:** Real-time change notification system

**Capabilities:**
- **Event Types:** INSERT, MODIFY, REMOVE
- **Image Types:** NEW_AND_OLD_IMAGES, NEW_IMAGE, OLD_IMAGE, KEYS_ONLY
- **Ordering:** Maintains strict ordering of changes
- **Retention:** 24 hours default (extendable to 7 days)

**Integration:** Triggers Lambda functions for event processing

### 3. **AWS Backup**
**Role:** Centralized backup management service

**Components:**
- **Backup Vault:** Logical container for backups
- **Backup Plan:** Defines backup schedule and retention
- **Recovery Points:** Individual backup snapshots
- **Restore Jobs:** Asynchronous restore operations

**API Methods Used:**
- `list_recovery_points_by_backup_vault()` - Find available recovery points
- `start_restore_job()` - Initiate table restoration

**Key Features:**
- **Cross-region backup** capability
- **Lifecycle management** (automatic deletion)
- **Compliance tagging** and reporting
- **Cost optimization** through tiered storage

### 4. **AWS Lambda**
**Role:** Serverless compute for automated recovery logic

**Configuration:**
- **Trigger:** DynamoDB Streams
- **Runtime:** Python 3.x
- **Memory:** Configurable (typically 128-512 MB)
- **Timeout:** Configurable (typically 30-300 seconds)

**Permissions Required:**
- `dynamodb:DescribeStream` - Read stream records
- `dynamodb:GetRecords` - Retrieve stream data
- `backup:ListRecoveryPointsByBackupVault` - Find backups
- `backup:StartRestoreJob` - Trigger restore

### 5. **IAM (Identity and Access Management)**
**Role:** Security and access control

**Roles Created:**
1. **Lambda Execution Role:**
   - Permissions for DynamoDB Streams access
   - Permissions for AWS Backup operations
   - CloudWatch Logs permissions for logging

2. **AWS Backup Restore Role:**
   - PassRole permissions for restore operations
   - DynamoDB restore permissions
   - Cross-account access if needed

**Security Best Practices:**
- Least privilege principle
- Role-based access control
- No hardcoded credentials
- Environment variable configuration

### 6. **CloudWatch Logs**
**Role:** Monitoring and debugging

**Capabilities:**
- **Lambda Execution Logs:** Function invocation details
- **Error Tracking:** Exception handling and debugging
- **Performance Monitoring:** Execution time and resource usage
- **Audit Trail:** Restore job tracking

**Log Information:**
- Event details from DynamoDB Streams
- Recovery point selection logic
- Restore job initiation confirmation
- Error messages and stack traces

---

## 🏗️ Architecture Overview

### Data Flow Diagram

```
┌─────────────────┐
│  DynamoDB Table │
│  (Primary Data) │
└────────┬────────┘
         │
         │ Changes (INSERT/MODIFY/REMOVE)
         │
         ▼
┌─────────────────┐
│ DynamoDB Streams│
│ (NEW_AND_OLD_   │
│  IMAGES)        │
└────────┬────────┘
         │
         │ Stream Events
         │
         ▼
┌─────────────────┐
│  Lambda Function│
│  (Change Monitor)│
└────────┬────────┘
         │
         │ Detection Logic
         │ (REMOVE events)
         │
         ▼
┌─────────────────┐
│   AWS Backup    │
│  (Restore Job)  │
└────────┬────────┘
         │
         │ Recovery Point Selection
         │
         ▼
┌─────────────────┐
│ Restored Table  │
│ (Timestamped)   │
└─────────────────┘
```

### Recovery Process Flow

1. **Normal Operation:**
   - DynamoDB table active with regular backups
   - AWS Backup creates snapshots every 12 hours
   - PITR enabled for continuous recovery points

2. **Deletion Event:**
   - User/application deletes item(s) from table
   - DynamoDB Stream captures REMOVE event
   - Stream includes OldImage (data before deletion)

3. **Lambda Trigger:**
   - Lambda function invoked by stream event
   - Event type checked (REMOVE)
   - OldImage extracted for logging

4. **Restore Initiation:**
   - Lambda queries AWS Backup for latest recovery point
   - Recovery points sorted by creation date (newest first)
   - Restore job triggered with timestamped target table

5. **Recovery Execution:**
   - AWS Backup asynchronously restores table
   - New table created with name: `{original}-restored-{timestamp}`
   - Restore job ID returned for tracking

6. **Verification:**
   - CloudWatch Logs capture restore initiation
   - AWS Backup console shows job status
   - Restored table available for validation

---

## 🔧 Technical Implementation Details

### Lambda Function Logic

#### Event Processing
```python
for record in event['Records']:
    event_name = record['eventName']   # INSERT, MODIFY, REMOVE
    old_image = record.get('dynamodb', {}).get('OldImage', {})
    new_image = record.get('dynamodb', {}).get('NewImage', {})
```

**Event Types:**
- **INSERT:** New item added (not critical for recovery)
- **MODIFY:** Existing item updated (could be corruption)
- **REMOVE:** Item deleted (critical - triggers restore)

#### Recovery Point Selection
```python
response = backup.list_recovery_points_by_backup_vault(
    BackupVaultName=VAULT_NAME,
    ByResourceType="DynamoDB"
)

latest = sorted(
    response['RecoveryPoints'],
    key=lambda x: x['CreationDate'],
    reverse=True
)[0]
```

**Selection Logic:**
- Filter by resource type (DynamoDB)
- Sort by creation date (descending)
- Select most recent recovery point
- Extract RecoveryPointArn for restore

#### Restore Job Initiation
```python
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
```

**Restore Parameters:**
- **RecoveryPointArn:** Identifies specific backup to restore
- **IamRoleArn:** Role with restore permissions
- **ResourceType:** DynamoDB
- **Metadata:** Source and target table names
- **Timestamp:** Ensures unique table names for multiple restores

### Backup Plan Configuration

#### Schedule Expression
```json
"ScheduleExpression": "cron(0 */12 * * ? *)"
```

**Cron Breakdown:**
- `0` - Minute (0)
- `*/12` - Hour (every 12 hours)
- `*` - Day of month (every day)
- `*` - Month (every month)
- `?` - Day of week (any)
- `*` - Year (every year)

**Result:** Backups at 00:00 and 12:00 daily

#### Lifecycle Management
```json
"Lifecycle": {
    "DeleteAfterDays": 35
}
```

**Retention Policy:**
- Backups retained for 35 days
- Automatic deletion after retention period
- Cost optimization through lifecycle management

#### Backup Windows
```json
"StartWindowMinutes": 60,
"CompletionWindowMinutes": 120
```

**Window Configuration:**
- **Start Window:** 60 minutes to initiate backup
- **Completion Window:** 120 minutes to complete backup
- **Flexibility:** Allows for resource contention and retries

### IAM Role Permissions

#### Lambda Execution Role
**Required Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeStream",
                "dynamodb:GetRecords",
                "dynamodb:GetShardIterator",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "backup:ListRecoveryPointsByBackupVault",
                "backup:StartRestoreJob"
            ],
            "Resource": "*"
        }
    ]
}
```

#### AWS Backup Restore Role
**Required Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::ACCOUNT_ID:role/AWS-Backup-Rrestore-Role"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:RestoreTableFromBackup"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 💡 Interview Talking Points

### Technical Questions

**Q: Why use DynamoDB Streams instead of CloudWatch Events?**
A: DynamoDB Streams provides item-level change data capture with both old and new images. CloudWatch Events operates at the API level and doesn't capture the actual data changes. Streams give us the exact state before and after modifications, which is critical for recovery logic.

**Q: What's the difference between NEW_AND_OLD_IMAGES and other stream view types?**
A: 
- **NEW_AND_OLD_IMAGES:** Captures both before and after state (used here)
- **NEW_IMAGE:** Only the new state after modification
- **OLD_IMAGE:** Only the old state before modification
- **KEYS_ONLY:** Only the primary key values

We use NEW_AND_OLD_IMAGES because we need the OldImage to understand what was deleted and validate the recovery.

**Q: Why trigger restore only on REMOVE events?**
A: REMOVE represents data deletion, which is the most critical data loss scenario. While MODIFY could indicate corruption, it's harder to determine if it's malicious or intentional. Deletion is almost always unintended in production systems and requires immediate recovery.

**Q: How do you handle restore job failures?**
A: The current implementation initiates the restore job asynchronously. For production, I would add:
- CloudWatch Alarms on restore job failures
- SNS notifications for failed restores
- Dead Letter Queue (DLQ) for Lambda failures
- Retry logic with exponential backoff
- Manual intervention workflow for critical failures

**Q: What's the RPO and RTO of this solution?**
A: 
- **RPO (Recovery Point Objective):** Up to 12 hours (backup schedule) or 35 days (PITR window)
- **RTO (Recovery Time Objective):** Seconds to initiate restore, minutes to complete depending on table size

PITR significantly improves RPO compared to scheduled backups alone.

**Q: How would you scale this for multiple tables?**
A: 
- Use AWS Backup resource tagging for multi-table selection
- Implement Lambda environment variable per table or configuration file
- Use AWS Backup plan with multiple resource selections
- Consider separate Lambda functions per table for isolation
- Implement table-specific restore strategies

**Q: Why use AWS Backup instead of DynamoDB's native backup?**
A: AWS Backup provides:
- Centralized backup management across multiple AWS services
- Compliance reporting and audit trails
- Lifecycle management and cost optimization
- Cross-region and cross-account backup capabilities
- Unified restore interface

DynamoDB native backups are service-specific and lack these enterprise features.

### Architecture Questions

**Q: How would you implement multi-region disaster recovery?**
A: 
- Enable cross-region copy in AWS Backup
- Deploy Lambda function in secondary region
- Use DynamoDB Global Tables for active-active replication
- Implement Route53 health checks for automatic failover
- Consider AWS Global Accelerator for low-latency access

**Q: What happens if the Lambda function fails during processing?**
A: DynamoDB Streams ensures at-least-once delivery. If Lambda fails:
- Stream retains records for 24 hours (configurable to 7 days)
- Lambda will retry based on configuration
- Failed invocations logged to CloudWatch
- Can implement DLQ for persistent failures

**Q: How do you prevent infinite restore loops?**
A: Current implementation creates timestamped tables, preventing loops. Additional safeguards:
- Check if restore already in progress
- Implement cooldown period between restores
- Add restore count limit per time window
- Use DynamoDB conditional writes for state management

**Q: How would you add approval workflow for restores?**
A: 
- Implement Step Functions state machine
- Add manual approval step before restore
- Use SNS for approval notifications
- Integrate with ServiceNow or Jira for ticket tracking
- Maintain audit trail of approvals

### Security Questions

**Q: How do you secure the restored data?**
A: 
- Restored tables inherit original table's IAM policies
- Implement table-level encryption at rest using AWS KMS
- Use VPC endpoints for private network access
- Enable DynamoDB encryption with customer-managed CMK
- Implement fine-grained access control with IAM conditions

**Q: What are the security risks of this approach?**
A: 
- Lambda execution role permissions (least privilege critical)
- Potential for unauthorized restore initiation
- Exposure of sensitive data in logs (OldImage)
- IAM role credential theft
- Cross-region data transfer risks

**Q: How do you ensure compliance with data privacy regulations?**
A: 
- Implement data classification and tagging
- Use encryption at rest and in transit
- Maintain audit logs of all restore operations
- Implement data retention policies
- Consider regional data residency requirements

### Operational Questions

**Q: How do you monitor the health of this DR solution?**
A: 
- CloudWatch Metrics for Lambda invocations and errors
- CloudWatch Alarms for restore job failures
- AWS Backup Dashboard for backup compliance
- DynamoDB CloudWatch metrics for table health
- Custom metrics for restore success rate

**Q: How do you test this DR solution?**
A: 
- Regular disaster recovery drills (monthly/quarterly)
- Automated testing using chaos engineering
- Restore time validation against RTO targets
- Data integrity validation post-restore
- Documentation of test results and improvements

**Q: What's the cost impact of this solution?**
A: 
- DynamoDB Streams costs (per GB of data)
- AWS Backup storage costs (per GB-month)
- Lambda invocation costs (per request + duration)
- CloudWatch Logs costs (per GB ingestion)
- Restored table storage costs (temporary)

Cost optimization: Use lifecycle policies, monitor backup sizes, optimize Lambda memory allocation.

---

## 🚀 Enhancement Opportunities

### Immediate Improvements

1. **Multi-Event Handling**
   - Add logic for MODIFY events (data corruption detection)
   - Implement pattern recognition for malicious changes
   - Add configurable event type filtering

2. **Restore Validation**
   - Automatic data integrity checks post-restore
   - Record count validation
   - Checksum verification for critical data

3. **Notification System**
   - SNS notifications for restore initiation
   - Slack integration for team alerts
   - Email notifications for compliance

4. **Metrics and Dashboard**
   - CloudWatch custom metrics for restore operations
   - Recovery time tracking
   - Success/failure rate monitoring

5. **Configuration Management**
   - Move hardcoded values to Parameter Store
   - Implement environment-specific configurations
   - Add configuration validation

### Advanced Features

1. **Intelligent Recovery**
   - Machine learning for anomaly detection
   - Automatic rollback for detected corruption
   - Predictive failure prevention

2. **Multi-Table Support**
   - Dynamic table discovery via tagging
   - Bulk restore capabilities
   - Table dependency management

3. **Compliance Integration**
   - Automated compliance reporting
   - Integration with AWS Audit Manager
   - Policy as Code for backup requirements

4. **Cost Optimization**
   - Intelligent backup frequency based on change rate
   - Tiered storage for long-term retention
   - Backup compression and deduplication

5. **Self-Service Portal**
   - Web interface for restore requests
   - Approval workflow integration
   - Restore history and audit trail

---

## 📊 Performance Characteristics

### Timing Analysis

| Operation | Typical Duration | Factors |
|-----------|-----------------|---------|
| DynamoDB Stream Processing | < 100ms | Record size, Lambda cold start |
| Recovery Point Query | 500ms - 2s | Number of recovery points |
| Restore Job Initiation | < 1s | AWS Backup API latency |
| Table Restore (Small) | 1-5 minutes | Table size, provisioned throughput |
| Table Restore (Large) | 10-60 minutes | Table size, provisioned throughput |

### Scalability Considerations

**Throughput:**
- DynamoDB Streams: Scales with table provisioned capacity
- Lambda: Concurrent executions up to account limit
- AWS Backup: Asynchronous, no direct throughput impact

**Storage:**
- DynamoDB Streams: 24-hour retention, charged per GB
- AWS Backup: Charged per GB-month, tiered pricing
- Restored Tables: Temporary storage, cleanup required

---

## 🎓 Key Learning Outcomes

### Technical Skills Demonstrated

- **Event-Driven Architecture:** Lambda with DynamoDB Streams
- **Serverless Computing:** AWS Lambda best practices
- **Backup and Recovery:** AWS Backup service utilization
- **IAM Security:** Role-based access control design
- **Cloud Monitoring:** CloudWatch Logs integration
- **API Integration:** Boto3 SDK for multiple AWS services

### Cloud Architecture Knowledge

- **Disaster Recovery Patterns:** Recovery Point/Time Objectives
- **Data Protection Strategies:** Backup, PITR, replication
- **High Availability Design:** Automated recovery mechanisms
- **Cost Optimization:** Lifecycle management and retention policies
- **Security Best Practices:** Least privilege, encryption, monitoring

### DevOps Practices

- **Infrastructure as Code:** JSON configuration for backup plans
- **Automation:** Elimination of manual recovery processes
- **Monitoring and Alerting:** CloudWatch integration
- **Documentation:** Architecture diagrams and runbooks
- **Testing:** Disaster recovery drill procedures

---

## 🔗 Additional Resources

### AWS Documentation
- [DynamoDB Streams](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html)
- [AWS Backup](https://docs.aws.amazon.com/awsbackup/latest/devguide/whatisbackup.html)
- [Lambda with DynamoDB Streams](https://docs.aws.amazon.com/lambda/latest/dg/with-ddb.html)
- [DynamoDB Point-in-Time Recovery](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/PointInTimeRecovery.html)

### Best Practices
- [AWS Disaster Recovery Framework](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html)
- [Well-Architected Framework - Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Backup and Recovery Best Practices](https://docs.aws.amazon.com/whitepapers/latest/aws-backup-best-practices/aws-backup-best-practices.html)

### Related Tools
- **AWS Disaster Recovery (DR) Solution:** Automated DR orchestration
- **AWS Elastic Disaster Recovery (DRS):** Physical and virtual machine recovery
- **AWS Site-to-Site VPN:** Multi-region connectivity
- **AWS Global Accelerator:** Cross-region performance optimization

---

## 💼 Interview Success Tips

### Technical Depth
1. **Know the data flow:** Be able to trace a deletion from DynamoDB to restored table
2. **Understand trade-offs:** Why this approach vs alternatives
3. **Explain limitations:** Current constraints and how to address them
4. **Discuss scaling:** How this grows with multiple tables/regions

### Business Value
1. **Connect to RPO/RTO:** Explain business impact of recovery objectives
2. **Cost justification:** Compare to manual recovery costs
3. **Compliance relevance:** Map to regulatory requirements
4. **Risk reduction:** Quantify data loss prevention value

### Problem-Solving
1. **Debugging approach:** How to troubleshoot failed restores
2. **Edge cases:** What happens with concurrent deletions
3. **Failure modes:** Lambda failures, backup unavailability
4. **Testing strategy:** How to validate DR effectiveness

### Communication
1. **Structure answers:** Situation, Action, Result format
2. **Use diagrams:** Draw architecture when explaining
3. **Be specific:** Reference actual code and configurations
4. **Show enthusiasm:** Demonstrate passion for cloud architecture

---

## 📝 Sample Interview Responses

### "Tell me about a challenging technical problem you solved"

"In my Disaster Recovery project, I needed to implement automated recovery for DynamoDB tables. The challenge was detecting deletions in real-time and triggering restores without manual intervention. I used DynamoDB Streams with NEW_AND_OLD_IMAGES to capture both before and after states, then built a Lambda function that processes REMOVE events. The function queries AWS Backup for the latest recovery point and initiates a restore job with a timestamped table name. This reduced RTO from hours to seconds and eliminated human error in recovery scenarios."

### "How do you approach system design for reliability?"

"I focus on the Well-Architected Framework's Reliability Pillar. For the DR project, I implemented multiple layers: automated backups every 12 hours, Point-in-Time Recovery for continuous recovery points, and event-driven restore automation. I also incorporated monitoring through CloudWatch Logs and implemented IAM roles with least privilege. The design considers both automated recovery (Lambda) and manual recovery (AWS Backup console) to ensure resilience against different failure scenarios."

### "What's your experience with AWS serverless technologies?"

"I've extensively used AWS Lambda for event-driven architectures. In the DR project, Lambda processes DynamoDB Stream events to trigger automated restores. I configured the Lambda with appropriate IAM roles, set environment variables for configuration, and integrated with CloudWatch for logging. I understand Lambda's scaling characteristics, cold starts, and best practices for memory and timeout configuration. I also use serverless for cost optimization and operational simplicity."

---

**Last Updated:** May 2026  
**Project Version:** 1.0  
**AWS SDK:** Boto3 latest  
**Python Version:** 3.x  
**Primary Region:** us-west-1
