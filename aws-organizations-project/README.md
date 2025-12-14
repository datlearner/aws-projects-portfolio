# 🚀 AWS Organizations – Real-World Enterprise Project

[![AWS](https://img.shields.io/badge/AWS-Cloud-orange?logo=amazon-aws)](https://aws.amazon.com/)  
[![License](https://img.shields.io/badge/License-MIT-green)](#)

---

## 📌 Project Overview
This project demonstrates how to design and implement a **secure, multi-account AWS Organization** following real enterprise best practices.  
It simulates how a growing company structures accounts, applies governance using **Service Control Policies (SCPs)**, and enforces security and cost controls at scale.

> Focused on **Cloud / Solutions Architect** and **DevOps** roles. This project emphasizes governance, security, and architecture, not just launching resources.

---

## 🏢 Business Scenario
**Company:** TechNova Ltd (fictional)

Challenges as the company grew:

- ❌ Poor security controls  
- ❌ No environment separation (Dev/Test/Prod)  
- ❌ High cloud costs  
- ❌ No centralized logging or auditing  

---

## 🎯 Goal
- Separate workloads into multiple accounts  
- Apply security guardrails with SCPs  
- Control costs and enforce approved regions  
- Follow AWS Well-Architected best practices  

---

## 🏗️ Organization Architecture

```mermaid
graph TD
    Root["Root"]
    SecurityOU["Security OU"]
    LogArchive["Log-Archive Account"]
    SecurityTooling["Security-Tooling Account"]
    InfrastructureOU["Infrastructure OU"]
    SharedServices["Shared-Services Account"]
    WorkloadsOU["Workloads OU"]
    Dev["Dev Account"]
    Test["Test Account"]
    Prod["Prod Account"]
    SandboxOU["Sandbox OU"]
    DevSandbox["Developer-Sandbox Account"]

    Root --> SecurityOU
    SecurityOU --> LogArchive
    SecurityOU --> SecurityTooling

    Root --> InfrastructureOU
    InfrastructureOU --> SharedServices

    Root --> WorkloadsOU
    WorkloadsOU --> Dev
    WorkloadsOU --> Test
    WorkloadsOU --> Prod

    Root --> SandboxOU
    SandboxOU --> DevSandbox



🔐 Service Control Policies (SCPs)

SCPs enforce maximum permissions across accounts. Even administrators cannot bypass them.

<details> <summary>1️⃣ Deny Root User Usage</summary>

Purpose: Prevent usage of AWS root user in all member accounts.

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


Attached to: All OUs except Management Account

</details> <details> <summary>2️⃣ Restrict AWS Regions</summary>

Purpose: Allow resources only in approved regions (us-east-1, eu-west-1).

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


Attached to: Workloads OU, Sandbox OU

</details> <details> <summary>3️⃣ Cost Control – Block Expensive Services in Dev</summary>

Purpose: Prevent high cloud bills in non-production accounts.

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


Attached to: Dev and Sandbox accounts

</details> <details> <summary>4️⃣ Protect Production Environment</summary>

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


Attached to: Prod Account only

</details>
👥 IAM Strategy
Role Name	Access	Purpose
DevOpsRole	Dev & Test	Full access for deployment & testing
ReadOnlySecurityRole	All accounts	Read-only security monitoring

Best Practices:

No IAM users in member accounts

Cross-account roles for access

Principle of least privilege

🧠 Key Learnings

How enterprises scale AWS securely

Importance of multi-account strategy

SCPs enforce governance at scale

Real-world cost and security controls

🚀 Next Improvements

Automate with Terraform

Integrate AWS Control Tower

Add budget alarms and cost reports
