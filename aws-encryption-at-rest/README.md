Encrypting Data at Rest with AWS Encryption Options
📌 Overview

This project demonstrates how to secure data at rest in AWS by using Amazon S3 default encryption, AWS Key Management Service (AWS KMS), and Amazon EBS encryption. It also highlights how to audit and monitor encryption activities with AWS CloudTrail.

🛠️ Prerequisites & Tools Used

AWS Account with appropriate permissions

AWS Services:

Amazon S3 (object storage & default encryption)

Amazon EC2 (compute instance for EBS attachment)

Amazon EBS (encrypted volumes)

AWS Key Management Service (KMS)

AWS CloudTrail (audit logging)

IAM Role/Policy with access to KMS, S3, EC2, and CloudTrail

AWS Management Console or AWS CLI for configuration

🎯 Objectives


Review the default encryption provided by Amazon S3.

Access an encrypted Amazon S3 object.

Create an AWS KMS customer managed key to encrypt and decrypt data at rest.

Create and attach an encrypted Amazon EBS volume to an Amazon EC2 instance.

Disable and re-enable an AWS KMS key and observe the effects on data access.

Monitor encryption key usage with AWS CloudTrail event history.

Review KMS key rotation policies.

## 🏗 Architecture Diagram  
![Architecture Diagram](images/architecture.png)



🛠️ Project Steps
1. Review Default S3 Encryption

2. Access Encrypted S3 Object

3. Create a KMS Customer Managed Key

4. Encrypt and Attach an EBS Volume

5. Key Lifecycle Management (Disable/Re-enable Key)

6. Monitor Key Usage with CloudTrail

7. Review Key Rotation

✅ Conclusion

In this project, I:

Reviewed default encryption in Amazon S3.

Accessed encrypted S3 objects.

Created and used an AWS KMS customer managed key.

Encrypted and attached an EBS volume to an EC2 instance.

Observed the effects of disabling and re-enabling a KMS key.

Monitored key usage with AWS CloudTrail.

Reviewed KMS key rotation.

This project demonstrates the importance of encryption at rest and shows how AWS services make it easier to implement strong security practices.
