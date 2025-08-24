Securing Applications with Amazon Cognito
Overview

Implementing authentication and authorization in web applications can be challenging. Amazon Cognito simplifies this by providing secure sign-up, sign-in, and access control features.

In this project, I configured an Amazon Cognito User Pool to manage users and their authentication, and an Amazon Cognito Identity Pool to authorize users when accessing protected AWS resources such as Amazon DynamoDB.

This lab builds upon an existing Node.js web application (“Birds App”), hosted on AWS Cloud9 and Amazon S3 (Static Website Hosting), by integrating Cognito for secure user access.

Objectives

✅ Created an Amazon Cognito User Pool

✅ Added users to the User Pool

✅ Integrated the User Pool with the Birds web application for authentication

✅ Configured an Amazon Cognito Identity Pool for authorization

✅ Updated the application to use temporary AWS credentials to access Amazon DynamoDB


Scenario: Birds Web Application

The Birds application allows students to record and explore bird sightings. It includes:

Public pages

Home page

Educational page

Protected pages (require authentication via Cognito):

Sightings page (view past reports)

Reporting page (submit new sightings)

Administrator page (admin-only features)

Starting Architecture

User requests a protected page from their browser.

Request is routed to the Node.js application server (Birds app).

Application redirects to Amazon Cognito Hosted UI.

Authentication flow:

Cognito User Pool authenticates the user.

An access token is issued and stored in browser local storage (default: 3,600s).

Application validates the token and returns the protected page.

Page is delivered to the browser via Amazon CloudFront.

Final Architecture (with Identity Pool Integration)

To support admin operations and DynamoDB queries, an Identity Pool was added.

User requests access to the admin page.

Request is routed to the Node.js server.

Application redirects to Amazon Cognito Hosted UI.

Authentication flow:

Cognito User Pool authenticates the user.

Access token is returned and stored in browser local storage.

Application validates the token and grants access to the admin page.

Page is delivered via CloudFront.

Admin initiates a query to Amazon DynamoDB.

Application exchanges the token with the Cognito Identity Pool, which issues temporary AWS credentials.

Application uses these credentials to query DynamoDB and returns the data to the protected admin page.

Key AWS Services Used

Amazon Cognito (User Pools & Identity Pools)

Amazon DynamoDB

Amazon CloudFront

Amazon S3 (Static Website Hosting)

AWS Cloud9 (development environment)

Lessons Learned

How to integrate Amazon Cognito for authentication and authorization.

Using Identity Pools to provide temporary AWS credentials.

Protecting application pages and controlling access to AWS resources.

Next Steps

Extend Cognito setup with Multi-Factor Authentication (MFA).

Add fine-grained access control policies in Identity Pool roles.

Enhance UI/UX of login and sign-up flows.
