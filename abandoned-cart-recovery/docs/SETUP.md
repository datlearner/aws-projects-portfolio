# Setup Guide — Abandoned Cart Recovery Engine

Step-by-step instructions to deploy this project on AWS Free Tier from scratch.
Estimated time: **45–60 minutes**. Estimated cost: **$0.00**.

---

## Step 1 — Verify an Email in SES

SES requires email verification before sending.

1. Go to **AWS Console → SES → Verified Identities**
2. Click **Create Identity → Email Address**
3. Enter your email → click **Create Identity**
4. Check your inbox and click the verification link
5. Note this email — it becomes your `SES_FROM_EMAIL` env var

> **SES Sandbox mode**: By default SES can only send to verified emails.
> For demo purposes, also verify your test recipient email.
> To send to anyone, request production access in SES console (takes ~24h).

---

## Step 2 — Create DynamoDB Table

1. Go to **DynamoDB → Tables → Create Table**
2. Settings:
   - Table name: `abandoned-carts`
   - Partition key: `cart_id` (String)
   - Table class: DynamoDB Standard
   - Capacity mode: **On-demand** (free tier friendly)
3. After creation → go to **Additional settings → Time to Live**
4. Enable TTL → attribute name: `ttl`
5. Click **Save**

---

## Step 3 — Create SQS FIFO Queues (3 queues)

Repeat these steps 3 times for: `cart-recovery-1h.fifo`, `cart-recovery-24h.fifo`, `cart-recovery-72h.fifo`

1. Go to **SQS → Create Queue**
2. Type: **FIFO**
3. Name: `cart-recovery-1h.fifo` (must end in `.fifo`)
4. Settings:
   - Visibility timeout: `300` seconds
   - Message retention: `4 days`
   - Content-based deduplication: ✅ enabled
5. **Dead-letter queue** tab:
   - Enable DLQ → Create new queue: `cart-recovery-1h-dlq.fifo`
   - Maximum receives: `3`
6. Click **Create Queue**
7. Note the **Queue URL** (you'll need it for Lambda env vars)

---

## Step 4 — Create IAM Role for Lambdas

1. Go to **IAM → Roles → Create Role**
2. Trusted entity: **Lambda**
3. Add these permissions policies:
   - `AmazonDynamoDBFullAccess`
   - `AmazonSQSFullAccess`
   - `AmazonSESFullAccess`
   - `CloudWatchLogsFullAccess`
4. Name the role: `abandoned-cart-lambda-role`
5. Click **Create Role**

> For production: scope down to least-privilege policies per Lambda.

---

## Step 5 — Deploy the 4 Lambda Functions

Repeat for each Lambda in `lambdas/`:

### Package the code
```bash
cd lambdas/detect_abandonment
zip -r function.zip handler.py
```

### Create Lambda
1. Go to **Lambda → Create Function**
2. Author from scratch
3. Settings:
   - Name: `detect-abandonment`
   - Runtime: **Python 3.11**
   - Architecture: x86_64
   - Execution role: `abandoned-cart-lambda-role`
4. Upload the zip: **Code → Upload from → .zip file**

### Set Environment Variables
Under **Configuration → Environment Variables**, add:

**detect-abandonment:**
```
DYNAMODB_TABLE       = abandoned-carts
SQS_QUEUE_1H_URL     = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-1h.fifo
SQS_QUEUE_24H_URL    = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-24h.fifo
SQS_QUEUE_72H_URL    = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-72h.fifo
```

**send-email:**
```
DYNAMODB_TABLE       = abandoned-carts
SES_FROM_EMAIL       = your-verified@email.com
UNSUBSCRIBE_BASE_URL = https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/cart/unsubscribe
SQS_QUEUE_1H_URL     = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-1h.fifo
SQS_QUEUE_24H_URL    = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-24h.fifo
SQS_QUEUE_72H_URL    = https://sqs.us-east-1.amazonaws.com/YOUR_ACCOUNT/cart-recovery-72h.fifo
```

**track-conversion:**
```
DYNAMODB_TABLE = abandoned-carts
```

**dashboard-api:**
```
DYNAMODB_TABLE = abandoned-carts
```

### Add SQS triggers to send-email Lambda
1. Open `send-email` Lambda → **Add trigger**
2. Source: **SQS**
3. Queue: `cart-recovery-1h.fifo`
4. Batch size: `1`
5. Repeat for `24h` and `72h` queues

---

## Step 6 — Create API Gateway

1. Go to **API Gateway → Create API → REST API**
2. Name: `cart-recovery-api`
3. Create these resources and methods:

| Method | Path | Lambda |
|--------|------|--------|
| POST | `/cart/abandon` | detect-abandonment |
| POST | `/cart/recover` | track-conversion |
| GET | `/dashboard` | dashboard-api |

For each:
- Create Resource → Create Method
- Integration type: Lambda Function
- Enable Lambda Proxy integration ✅
- Select your Lambda function

4. **Deploy API**:
   - Actions → Deploy API
   - Stage name: `prod`
   - Note the **Invoke URL** — this is your API base URL

---

## Step 7 — Set a Budget Alert

1. Go to **AWS Billing → Budgets → Create Budget**
2. Type: Cost Budget
3. Amount: `$5`
4. Alert at 80% → email notification
5. This ensures you're notified before hitting any unexpected charges

---

## Step 8 — Test the Full Flow

```bash
# 1. Abandon a cart
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/cart/abandon \
  -H "Content-Type: application/json" \
  -d @sample_payloads/abandon_cart.json

# 2. Check DynamoDB — confirm cart saved
# (AWS Console → DynamoDB → abandoned-carts → Explore Items)

# 3. Wait for email (1h delay in prod; set to 60s for testing by editing send_after_ts logic)

# 4. Simulate recovery
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/cart/recover \
  -H "Content-Type: application/json" \
  -d @sample_payloads/recover_cart.json

# 5. Check dashboard
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/dashboard
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| SES not sending | Check email is verified in SES; check SES sandbox mode |
| Lambda timeout | Increase timeout to 30s in Lambda Configuration |
| SQS not triggering Lambda | Check Lambda trigger is enabled; check IAM permissions |
| DynamoDB errors | Verify table name matches env var exactly |
| 502 from API Gateway | Check Lambda logs in CloudWatch for errors |

