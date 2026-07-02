"""
Lambda: detect_abandonment
Triggered by: POST /cart/abandon (API Gateway)

Receives a cart abandonment event from the storefront,
saves it to DynamoDB, and starts a Step Functions execution
that orchestrates the 3-email recovery sequence.
"""

import json
import os
import uuid
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
sfn = boto3.client("stepfunctions")

TABLE_NAME        = os.environ["DYNAMODB_TABLE"]
STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        required = ["customer_email", "customer_name", "cart_items", "cart_total"]
        missing = [f for f in required if f not in body]
        if missing:
            return response(400, {"error": f"Missing required fields: {missing}"})

        cart_id        = body.get("cart_id", str(uuid.uuid4()))
        customer_email = body["customer_email"]
        customer_name  = body["customer_name"]
        cart_items     = body["cart_items"]
        cart_total     = body["cart_total"]
        store_name     = body.get("store_name", "Our Store")
        recover_url    = body.get("recover_url", "https://yourstore.com/cart")
        now            = datetime.now(timezone.utc).isoformat()

        table = dynamodb.Table(TABLE_NAME)

        try:
            table.put_item(
                Item={
                    "cart_id":        cart_id,
                    "customer_email": customer_email,
                    "customer_name":  customer_name,
                    "cart_items":     cart_items,
                    "cart_total":     str(cart_total),
                    "store_name":     store_name,
                    "recover_url":    recover_url,
                    "status":         "ABANDONED",
                    "emails_sent":    [],
                    "created_at":     now,
                    "updated_at":     now,
                    "ttl":            int(datetime.now(timezone.utc).timestamp()) + (30 * 24 * 60 * 60),
                },
                ConditionExpression="attribute_not_exists(cart_id)"
            )
        except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            print(f"Cart {cart_id} already exists — skipping duplicate")
            return response(200, {"cart_id": cart_id, "status": "ALREADY_QUEUED"})

        sfn_input = {
            "cart_id":        cart_id,
            "customer_email": customer_email,
            "customer_name":  customer_name,
            "cart_items":     cart_items,
            "cart_total":     str(cart_total),
            "store_name":     store_name,
            "recover_url":    recover_url,
        }

        sfn.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            name=f"cart-{cart_id}",
            input=json.dumps(sfn_input),
        )

        print(f"[detect_abandonment] Cart {cart_id} saved, Step Functions execution started")

        return response(200, {
            "cart_id": cart_id,
            "status":  "QUEUED",
            "message": "Cart abandonment recorded. Recovery flow started.",
        })

    except Exception as e:
        print(f"[detect_abandonment] ERROR: {str(e)}")
        return response(500, {"error": "Internal server error", "detail": str(e)})


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type":                "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }
