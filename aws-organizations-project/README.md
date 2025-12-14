AWS Organizations – Real-World Enterprise Project
📌 Project Overview

This project demonstrates how to design and implement a secure, multi-account AWS Organization following real enterprise best practices. It simulates how a growing company structures accounts, applies governance using Service Control Policies (SCPs), and enforces security and cost controls at scale.

🏢 Business Scenario

Company: TechNova Ltd (fictional)

TechNova started with a single AWS account. As the company grew, they faced:

Poor security controls

No environment separation (Dev/Test/Prod)

High cloud costs

No centralized logging or auditing

🎯 Goal

Design an AWS Organization that:

Separates workloads into multiple accounts

Applies security guardrails using SCPs

Controls costs and regions

Follows AWS Well-Architected best practices

🏗️ Organization Architecture
Root
│
├── Security OU
│ ├── Log-Archive Account
│ └── Security-Tooling Account
│
├── Infrastructure OU
│ └── Shared-Services Account
│
├── Workloads OU
│ ├── Dev Account
│ ├── Test Account
│ └── Prod Account
│
└── Sandbox OU
└── Developer-Sandbox Account

🔐 Service Control Policies (SCPs)

SCPs are used to define maximum permissions across accounts. Even administrators cannot bypass them.

1️⃣ Deny Root User Usage

Purpose: Prevent usage of the AWS root user in all member accounts.

{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "DenyRootUser",
"Effect": "Deny",
"Action": "*",
"Resource": "*",
"Condition": {
"StringEquals": {
"aws:PrincipalType": "Root"
}
}
}
]
}

📌 Attached to: All OUs except Management Account

2️⃣ Restrict AWS Regions

Purpose: Enforce compliance and cost control by allowing resources only in approved regions.

Allowed Regions: us-east-1, eu-west-1


📌 Attached to: All OUs except Management Account

2️⃣ Restrict AWS Regions

Purpose: Enforce compliance and cost control by allowing resources only in approved regions.

Allowed Regions: us-east-1, eu-west-1

📌 Attached to: All OUs except Management Account

2️⃣ Restrict AWS Regions

Purpose: Enforce compliance and cost control by allowing resources only in approved regions.

Allowed Regions: us-east-1, eu-west-1

{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "DenyOtherRegions",
"Effect": "Deny",
"NotAction": [
"iam:*",
"organizations:*",
"route53:*",
"cloudfront:*"
],
"Resource": "*",
"Condition": {
"StringNotEquals": {
"aws:RequestedRegion": [
"us-east-1",
"eu-west-1"
]
}
}
}
]
}

📌 Attached to: Workloads OU, Sandbox OU

3️⃣ Cost Control – Block Expensive Services in Dev

Purpose: Prevent accidental high cloud bills in non-production accounts.

{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "DenyExpensiveServices",
"Effect": "Deny",
"Action": [
"sagemaker:*",
"redshift:*",
"elasticmapreduce:*"
],
"Resource": "*"
}
]
}

📌 Attached to: Dev and Sandbox accounts

4️⃣ Protect Production Environment

Purpose: Prevent deletion of critical production resources.

{
"Version": "2012-10-17",
"Statement": [
{
"Sid": "DenyDeleteInProd",
"Effect": "Deny",
"Action": [
"ec2:TerminateInstances",
"rds:DeleteDBInstance",
"s3:DeleteBucket"
],
"Resource": "*"
}
]
}

📌 Attached to: Prod Account only

👥 IAM Strategy

No IAM users in member accounts

Cross-account IAM roles used for access

Principle of least privilege enforced

Example roles:

DevOpsRole → Dev & Test

ReadOnlySecurityRole → All accounts

🧠 Key Learnings

How enterprises scale AWS securely

Why multi-account strategy is critical

How SCPs enforce governance at scale

Real-world cost and security controls

🚀 Next Improvements

Automate with Terraform

Integrate AWS Control Tower

Add budget alarms and cost reports
