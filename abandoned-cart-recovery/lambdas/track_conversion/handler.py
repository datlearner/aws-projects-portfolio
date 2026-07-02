"""
Lambda: track_conversion
Triggered by: POST /cart/recover (API Gateway)

Called by the storefront when a customer completes a purchase.
Updates cart status to RECOVERED in DynamoDB so Step Functions
stops sending emails on next check.
"""

import json
import os
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE"]


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        cart_id        = body.get("cart_id")
        order_id       = body.get("order_id", "UNKNOWN")
        order_total    = body.get("order_total")
        converted_from = body.get("converted_from", "DIRECT")  # "1h", "24h", "72h", or "DIRECT"

        if not cart_id:
            return response(400, {"error": "cart_id is required"})

        table  = dynamodb.Table(TABLE_NAME)
        result = table.get_item(Key={"cart_id": cart_id})
        cart   = result.get("Item")

        if not cart:
            return response(404, {"error": f"Cart {cart_id} not found"})

        if cart["status"] == "RECOVERED":
            return response(200, {"cart_id": cart_id, "status": "ALREADY_RECOVERED"})

        table.update_item(
            Key={"cart_id": cart_id},
            UpdateExpression="""
                SET #status = :recovered,
                    order_id = :order_id,
                    order_total = :order_total,
                    converted_from = :converted_from,
                    recovered_at = :now,
                    updated_at = :now
            """,
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":recovered":      "RECOVERED",
                ":order_id":       order_id,
                ":order_total":    str(order_total) if order_total else cart.get("cart_total"),
                ":converted_from": converted_from,
                ":now":            datetime.now(timezone.utc).isoformat(),
            },
        )

        print(f"[track_conversion] Cart {cart_id} RECOVERED via {converted_from} → order {order_id}")

        return response(200, {
            "cart_id":        cart_id,
            "status":         "RECOVERED",
            "order_id":       order_id,
            "converted_from": converted_from,
        })

    except Exception as e:
        print(f"[track_conversion] ERROR: {str(e)}")
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
