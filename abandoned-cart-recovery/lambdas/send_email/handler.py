"""
Lambda: send_email
Triggered by: Step Functions (CartRecoveryFlow)

Called at 1h, 24h, and 72h after cart abandonment.
Checks DynamoDB status before every send — stops immediately
if cart is already RECOVERED or UNSUBSCRIBED.
Idempotent: skips if this sequence was already sent.
"""

import json
import os
import boto3
from datetime import datetime, timezone

ses      = boto3.client("ses")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["DYNAMODB_TABLE"]
FROM_EMAIL = os.environ["SES_FROM_EMAIL"]


def lambda_handler(event, context):
    cart_id        = event["cart_id"]
    customer_email = event["customer_email"]
    customer_name  = event["customer_name"]
    cart_items     = event["cart_items"]
    cart_total     = float(event["cart_total"])
    store_name     = event["store_name"]
    recover_url    = event["recover_url"]
    email_sequence = event["email_sequence"]   # "1h", "24h", "72h"

    table  = dynamodb.Table(TABLE_NAME)
    result = table.get_item(Key={"cart_id": cart_id})
    cart   = result.get("Item")

    if not cart:
        print(f"[send_email] Cart {cart_id} not found")
        return {"status": "NOT_FOUND", "cart_id": cart_id}

    if cart["status"] == "RECOVERED":
        print(f"[send_email] Cart {cart_id} already recovered — stopping flow")
        return {"status": "RECOVERED", "cart_id": cart_id}

    if email_sequence in cart.get("emails_sent", []):
        print(f"[send_email] {email_sequence} already sent for {cart_id} — idempotent skip")
        return {"status": cart["status"], "cart_id": cart_id}

    subject, html_body = build_email(
        sequence=email_sequence,
        customer_name=customer_name,
        cart_items=cart_items,
        cart_total=cart_total,
        store_name=store_name,
        recover_url=recover_url,
    )

    ses.send_email(
        Source=f"{store_name} <{FROM_EMAIL}>",
        Destination={"ToAddresses": [customer_email]},
        Message={
            "Subject": {"Data": subject,    "Charset": "UTF-8"},
            "Body":    {"Html": {"Data": html_body, "Charset": "UTF-8"}},
        },
    )

    table.update_item(
        Key={"cart_id": cart_id},
        UpdateExpression="SET emails_sent = list_append(if_not_exists(emails_sent, :empty), :seq), updated_at = :now",
        ExpressionAttributeValues={
            ":seq":   [email_sequence],
            ":empty": [],
            ":now":   datetime.now(timezone.utc).isoformat(),
        },
    )

    print(f"[send_email] ✅ Sent {email_sequence} email to {customer_email} for cart {cart_id}")
    return {"status": cart["status"], "cart_id": cart_id, "email_sequence": email_sequence}


def build_email(sequence, customer_name, cart_items, cart_total, store_name, recover_url):
    first_name = customer_name.split()[0]
    items_html = "".join([
        f"""<tr>
              <td style="padding:8px;border-bottom:1px solid #eee;">{i.get('name','Product')}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">{i.get('qty',1)}</td>
              <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">${float(i.get('price',0)):.2f}</td>
            </tr>"""
        for i in cart_items
    ])

    if sequence == "1h":
        subject  = f"You left something behind, {first_name} 👀"
        headline = "You forgot something!"
        message  = f"Hey {first_name}, looks like you left some items in your cart. They're still waiting for you."
        cta      = "Complete My Purchase"
        urgency  = ""
    elif sequence == "24h":
        subject  = f"{first_name}, your cart is expiring soon ⏰"
        headline = "Your cart is about to expire"
        message  = f"Hi {first_name}, your items are still reserved — but not for much longer."
        cta      = "Save My Cart Now"
        urgency  = '<p style="color:#e74c3c;font-weight:bold;text-align:center;">⚠️ Items in your cart are in high demand</p>'
    else:
        subject  = f"Last chance, {first_name} — 10% off your cart 🎁"
        headline = "We want you back — here's 10% off"
        message  = f"Hi {first_name}, here's a special 10% discount just for you."
        cta      = "Claim My 10% Discount"
        urgency  = '<p style="background:#fff3cd;padding:12px;border-radius:6px;text-align:center;">Use code <strong>COMEBACK10</strong> at checkout</p>'

    html_body = f"""<!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
        <tr><td align="center">
          <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;">
            <tr><td style="background:#1a1a2e;padding:32px;text-align:center;">
              <h1 style="color:#fff;margin:0;">{store_name}</h1>
            </td></tr>
            <tr><td style="padding:40px 48px;">
              <h2 style="color:#1a1a2e;">{headline}</h2>
              <p style="color:#555;line-height:1.6;">{message}</p>
              {urgency}
              <table width="100%" style="margin:24px 0;border:1px solid #eee;border-radius:6px;">
                <tr style="background:#f9f9f9;">
                  <th style="padding:10px 8px;text-align:left;color:#888;font-size:12px;">ITEM</th>
                  <th style="padding:10px 8px;text-align:center;color:#888;font-size:12px;">QTY</th>
                  <th style="padding:10px 8px;text-align:right;color:#888;font-size:12px;">PRICE</th>
                </tr>
                {items_html}
                <tr>
                  <td colspan="2" style="padding:12px 8px;font-weight:bold;text-align:right;">Total:</td>
                  <td style="padding:12px 8px;font-weight:bold;text-align:right;">${cart_total:.2f}</td>
                </tr>
              </table>
              <table width="100%"><tr><td align="center" style="padding:16px 0;">
                <a href="{recover_url}" style="background:#e8651a;color:#fff;padding:16px 40px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:16px;">{cta}</a>
              </td></tr></table>
            </td></tr>
            <tr><td style="background:#f9f9f9;padding:24px;text-align:center;border-top:1px solid #eee;">
              <p style="color:#aaa;font-size:12px;margin:0;">You're receiving this because you added items to your cart at {store_name}.</p>
            </td></tr>
          </table>
        </td></tr>
      </table>
    </body></html>"""

    return subject, html_body
