"""
Tests for detect_abandonment Lambda.
Run with: pytest tests/ -v
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../lambdas/detect_abandonment"))

SAMPLE_CART = {
    "cart_id":        "test-cart-001",
    "customer_email": "customer@example.com",
    "customer_name":  "Jane Smith",
    "store_name":     "Demo Store",
    "recover_url":    "https://demostore.com/cart/test-cart-001",
    "cart_total":     149.99,
    "cart_items": [
        {"product_id": "SKU-001", "name": "Running Shoes", "price": 99.99, "qty": 1},
        {"product_id": "SKU-002", "name": "Water Bottle",  "price": 24.99, "qty": 2},
    ]
}

ENV_VARS = {
    "DYNAMODB_TABLE":    "abandoned-carts",
    "SQS_QUEUE_1H_URL":  "https://sqs.us-east-1.amazonaws.com/123/cart-recovery-1h.fifo",
    "SQS_QUEUE_24H_URL": "https://sqs.us-east-1.amazonaws.com/123/cart-recovery-24h.fifo",
    "SQS_QUEUE_72H_URL": "https://sqs.us-east-1.amazonaws.com/123/cart-recovery-72h.fifo",
}


@patch.dict(os.environ, ENV_VARS)
@patch("handler.dynamodb")
@patch("handler.sqs")
def test_valid_cart_abandonment(mock_sqs, mock_dynamo):
    """Valid cart abandonment should return 200 and queue 3 emails."""
    import handler

    mock_table = MagicMock()
    mock_dynamo.Table.return_value = mock_table
    mock_sqs.send_message.return_value = {"MessageId": "mock-id"}

    event = {"body": json.dumps(SAMPLE_CART)}
    result = handler.lambda_handler(event, {})

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["status"] == "QUEUED"
    assert body["cart_id"] == "test-cart-001"
    assert len(body["emails_scheduled"]) == 3

    # Verify 3 SQS messages were sent
    assert mock_sqs.send_message.call_count == 3

    # Verify DynamoDB put_item was called
    mock_table.put_item.assert_called_once()


@patch.dict(os.environ, ENV_VARS)
@patch("handler.dynamodb")
@patch("handler.sqs")
def test_missing_required_fields(mock_sqs, mock_dynamo):
    """Missing required fields should return 400."""
    import handler

    event = {"body": json.dumps({"customer_email": "test@example.com"})}
    result = handler.lambda_handler(event, {})

    assert result["statusCode"] == 400
    body = json.loads(result["body"])
    assert "Missing required fields" in body["error"]
    mock_sqs.send_message.assert_not_called()


@patch.dict(os.environ, ENV_VARS)
@patch("handler.dynamodb")
@patch("handler.sqs")
def test_auto_generates_cart_id(mock_sqs, mock_dynamo):
    """If no cart_id provided, one should be auto-generated."""
    import handler

    mock_table = MagicMock()
    mock_dynamo.Table.return_value = mock_table

    cart_without_id = {k: v for k, v in SAMPLE_CART.items() if k != "cart_id"}
    event = {"body": json.dumps(cart_without_id)}
    result = handler.lambda_handler(event, {})

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert "cart_id" in body
    assert len(body["cart_id"]) > 0


@patch.dict(os.environ, ENV_VARS)
@patch("handler.dynamodb")
@patch("handler.sqs")
def test_sqs_messages_have_correct_sequences(mock_sqs, mock_dynamo):
    """Each SQS message should contain the correct email_sequence label."""
    import handler

    mock_table = MagicMock()
    mock_dynamo.Table.return_value = mock_table

    event = {"body": json.dumps(SAMPLE_CART)}
    handler.lambda_handler(event, {})

    calls = mock_sqs.send_message.call_args_list
    sequences = [json.loads(c.kwargs["MessageBody"])["email_sequence"] for c in calls]
    assert sorted(sequences) == ["1h", "24h", "72h"]
