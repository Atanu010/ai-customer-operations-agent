from __future__ import annotations

EVALUATION_DATASET = [
    {"message": "Where is my order 1001?", "expected_intent": "ORDER_STATUS", "expected_tool": "get_order_status", "customer_id": 1},
    {"message": "What did I purchase in order 1002?", "expected_intent": "ORDER_DETAILS", "expected_tool": "get_order_details", "customer_id": 1},
    {"message": "My package is delayed and I need the status for order 1003.", "expected_intent": "DELIVERY_DELAY", "expected_tool": "get_order_status", "customer_id": 2},
    {"message": "Can I return an item after delivery?", "expected_intent": "RETURN_POLICY", "expected_tool": "search_knowledge_base", "customer_id": 2},
    {"message": "I need help with my customer account.", "expected_intent": "GENERAL_SUPPORT", "expected_tool": "search_knowledge_base", "customer_id": 3},
    {"message": "Show me all orders for customer 2.", "expected_intent": "ORDER_DETAILS", "expected_tool": "get_customer_orders", "customer_id": 2},
    {"message": "Check the status of order 1005.", "expected_intent": "ORDER_STATUS", "expected_tool": "get_order_status", "customer_id": 1},
    {"message": "I want to know the refund policy.", "expected_intent": "RETURN_POLICY", "expected_tool": "search_knowledge_base", "customer_id": 2},
    {"message": "My order 1001 has not arrived on time.", "expected_intent": "DELIVERY_DELAY", "expected_tool": "get_order_status", "customer_id": 1},
    {"message": "Tell me about cancellation policy.", "expected_intent": "RETURN_POLICY", "expected_tool": "search_knowledge_base", "customer_id": 3},
]
