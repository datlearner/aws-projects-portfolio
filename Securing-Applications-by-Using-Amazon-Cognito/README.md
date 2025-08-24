# Securing Applications with Amazon Cognito

## Overview
Implementing authentication and authorization in web applications can be challenging. **Amazon Cognito** simplifies this by providing secure sign-up, sign-in, and access control features.

In this project, I configured an **Amazon Cognito User Pool** to manage users and their authentication, and an **Amazon Cognito Identity Pool** to authorize users when accessing protected AWS resources such as **Amazon DynamoDB**.

This project builds upon an existing Node.js web application (“Birds App”), hosted on **AWS Cloud9** and **Amazon S3 (Static Website Hosting)**, by integrating Cognito for secure user access.

---

## Objectives
- ✅ Created an Amazon Cognito User Pool  
- ✅ Added users to the User Pool  
- ✅ Integrated the User Pool with the Birds web application for authentication  
- ✅ Configured an Amazon Cognito Identity Pool for authorization  
- ✅ Updated the application to use temporary AWS credentials to access Amazon DynamoDB  

---

## Scenario: Birds Web Application
The Birds application allows students to record and explore bird sightings. It includes:

**Public pages:**  
- Home page  
- Educational page  

**Protected pages (require authentication via Cognito):**  
- Sightings page (view past reports)  
- Reporting page (submit new sightings)  
- Administrator page (admin-only features)  

---

## Architecture

### Starting Architecture
1. User requests a protected page from their browser.  
2. Request is routed to the **Node.js application server** (Birds app).  
3. Application redirects to **Amazon Cognito Hosted UI**.  
4. **Authentication flow:**  
   - Cognito User Pool authenticates the user  
   - Access token is issued and stored in browser local storage (default: 3,600s)  
   - Application validates the token and returns the protected page  
5. Page is delivered to the browser via **Amazon CloudFront**  

### Final Architecture (with Identity Pool Integration)
1. User requests access to the **admin page**.  
2. Request is routed to the Node.js server.  
3. Application redirects to **Amazon Cognito Hosted UI**.  
4. **Authentication flow:**  
   - Cognito User Pool authenticates the user  
   - Access token is returned and stored in browser local storage  
   - Application validates the token and grants access to the admin page  
5. Page is delivered via **CloudFront**  
6. Admin initiates a query to **Amazon DynamoDB**  
7. Application exchanges the token with the **Cognito Identity Pool**, which issues temporary AWS credentials  
8. Application uses these credentials to query DynamoDB and return data to the protected admin page  

**Architecture Diagram:**  
![Architecture Diagram](diagrams/architecture.png)

---

## Key AWS Services Used
- **Amazon Cognito** (User Pools & Identity Pools)  
- **Amazon DynamoDB**  
- **Amazon CloudFront**  
- **Amazon S3** (Static Website Hosting)  
- **AWS Cloud9** (development environment)  

---

## Lessons Learned
- How to integrate **Amazon Cognito** for authentication and authorization  
- Using **Identity Pools** to provide temporary AWS credentials  
- Protecting application pages and controlling access to AWS resources  

---

## Next Steps
- Extend Cognito setup with **Multi-Factor Authentication (MFA)**  
- Add fine-grained access control policies in Identity Pool roles  
- Enhance UI/UX of login and sign-up flows  

---

