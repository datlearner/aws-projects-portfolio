"""
Lambda: dashboard_api
Triggered by: GET /dashboard (API Gateway)

Scans DynamoDB and returns aggregated business metrics:
- Total carts abandoned vs recovered
- Recovery rate and estimated revenue recovered
- Per-sequence email performance (1h, 24h, 72h)
- Top abandoned products
"""

import json
import os
import boto3
from collections import defaultdict
from decimal import Decimal

dynamodb  = boto3.resource("dynamodb")
TABLE_NAME = os.environ["DYNAMODB_TABLE"]


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def lambda_handler(event, context):
    try:
        table = dynamodb.Table(TABLE_NAME)

        # Scan all carts (fine at demo/portfolio scale)
        items    = []
        response = table.scan()
        items.extend(response.get("Items", []))
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        total_abandoned  = len(items)
        total_recovered  = sum(1 for i in items if i.get("status") == "RECOVERED")
        recovery_rate    = (total_recovered / total_abandoned * 100) if total_abandoned else 0
        revenue_recovered = sum(
            float(i.get("order_total", i.get("cart_total", 0)))
            for i in items if i.get("status") == "RECOVERED"
        )

        seq_sent      = defaultdict(int)
        seq_converted = defaultdict(int)
        for item in items:
            for seq in item.get("emails_sent", []):
                seq_sent[seq] += 1
                if item.get("converted_from") == seq:
                    seq_converted[seq] += 1

        email_performance = {}
        for seq in ["1h", "24h", "72h"]:
            sent      = seq_sent[seq]
            converted = seq_converted[seq]
            email_performance[f"email_{seq}"] = {
                "sent":            sent,
                "converted":       converted,
                "conversion_rate": f"{(converted / sent * 100):.1f}%" if sent else "0.0%",
            }

        product_counts = defaultdict(lambda: {"name": "", "count": 0})
        for item in items:
            for product in item.get("cart_items", []):
                pid = product.get("product_id", "UNKNOWN")
                product_counts[pid]["name"]  = product.get("name", "Unknown Product")
                product_counts[pid]["count"] += 1

        top_products = sorted(
            [{"product_id": k, "name": v["name"], "abandoned_count": v["count"]}
             for k, v in product_counts.items()],
            key=lambda x: x["abandoned_count"],
            reverse=True
        )[:10]

        dashboard = {
            "summary": {
                "total_abandoned":            total_abandoned,
                "total_recovered":            total_recovered,
                "recovery_rate":              f"{recovery_rate:.1f}%",
                "estimated_revenue_recovered": f"${revenue_recovered:,.2f}",
            },
            "email_performance":      email_performance,
            "top_abandoned_products": top_products,
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type":                "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(dashboard, cls=DecimalEncoder, indent=2),
        }

    except Exception as e:
        print(f"[dashboard_api] ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
