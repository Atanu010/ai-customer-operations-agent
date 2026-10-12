from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.llm.base import BaseLLMProvider, IntentClassification, ToolCall


class MockLLMProvider(BaseLLMProvider):
    INTENT_PATTERNS = {
        "ORDER_STATUS": ["status", "where is my order", "check order", "track my order", "delivery status"],
        "ORDER_DETAILS": ["details", "what did i order", "what did i buy", "product", "order details", "items", "buy", "purchase"],
        "DELIVERY_DELAY": ["delay", "late", "not arrived", "delayed", "arrived late"],
        "RETURN_POLICY": ["return", "refund", "cancel", "exchange", "policy"],
        "GENERAL_SUPPORT": ["help", "support", "issue", "question"],
    }

    async def classify_intent(self, message: str) -> IntentClassification:
        normalized = (message or "").lower()
        order_match = re.search(r"order\s*(?:id|number)?\s*#?(\d+)", normalized)
        order_id = int(order_match.group(1)) if order_match else None
        best_intent = "UNKNOWN"
        best_score = 0
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if pattern in normalized:
                    score += 1
            if "order" in normalized and "status" in normalized:
                score += 3
            if "what did" in normalized and "order" in normalized:
                score += 3
            if "buy" in normalized or "purchase" in normalized:
                score += 2
            if "return" in normalized and "item" in normalized:
                score += 2
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent == "UNKNOWN":
            ordered_words = [word for word in normalized.split() if word.isdigit()]
            if ordered_words:
                best_intent = "ORDER_STATUS"

        requires_tool = best_intent in {"ORDER_STATUS", "ORDER_DETAILS", "DELIVERY_DELAY", "RETURN_POLICY"}
        confidence = 0.92 if best_intent != "UNKNOWN" else 0.28
        return IntentClassification(
            intent=best_intent,
            order_id=order_id,
            confidence=confidence,
            requires_tool=requires_tool,
        )

    async def select_tools(self, message: str, tools: list[dict[str, Any]] | None = None) -> list[ToolCall]:
        normalized = (message or "").lower()
        order_match = re.search(r"order\s*(?:id|number)?\s*#?(\d+)", normalized)
        order_id = int(order_match.group(1)) if order_match else None
        customer_match = re.search(r"customer\s*(?:id|number)?\s*#?(\d+)", normalized)
        customer_id = int(customer_match.group(1)) if customer_match else None

        if "all orders" in normalized or "orders for customer" in normalized or "show me all orders" in normalized:
            return [ToolCall(tool_name="get_customer_orders", arguments={"customer_id": customer_id or 1})]
        if "what did i buy" in normalized or "what did i purchase" in normalized or "order details" in normalized:
            return [ToolCall(tool_name="get_order_details", arguments={"order_id": order_id or 1001})]
        if "return" in normalized or "refund" in normalized or "cancel" in normalized or "policy" in normalized:
            return [ToolCall(tool_name="search_knowledge_base", arguments={"query": "return refund cancellation policy"})]
        if "delay" in normalized or "late" in normalized or "not arrived" in normalized:
            return [ToolCall(tool_name="get_order_status", arguments={"order_id": order_id or 1001})]
        if "status" in normalized or "where is my order" in normalized or "check order" in normalized:
            return [ToolCall(tool_name="get_order_status", arguments={"order_id": order_id or 1001})]
        if "help" in normalized or "support" in normalized or "issue" in normalized:
            return [ToolCall(tool_name="search_knowledge_base", arguments={"query": "customer support help"})]
        return []

    async def generate_response(self, *, message: str, intent: str, tool_result: dict[str, Any] | None = None) -> dict[str, Any]:
        tool_result = tool_result or {}
        answer = "I can help with that."
        if intent == "ORDER_STATUS":
            order = tool_result.get("order")
            if order:
                answer = f"Your order {order.get('id')} is currently {order.get('status')}."
        elif intent == "ORDER_DETAILS":
            order = tool_result.get("order")
            if order:
                answer = f"Your order includes {order.get('product_name')} and is tracked by {order.get('tracking_number') or 'n/a'}."
        elif intent == "DELIVERY_DELAY":
            answer = "I can help review the delivery timeline and any delays for your shipment."
        elif intent == "RETURN_POLICY":
            answer = "Eligible returns can be initiated within 30 days of delivery for unopened items."
        elif intent == "GENERAL_SUPPORT":
            answer = "I’ve reviewed the request and can continue with support guidance."
        else:
            answer = "I’m not sure I can help with that request. A human agent may be needed."

        return {
            "intent": intent,
            "answer": answer,
            "actions_taken": ["intent_classified", *([tool_result.get("tool_name")] if tool_result.get("tool_name") else [])],
            "order_id": tool_result.get("order_id"),
            "confidence": 0.9,
            "requires_human": intent == "UNKNOWN",
            "requires_tool": bool(tool_result.get("tool_name")),
            "tool_used": tool_result.get("tool_name"),
        }

    async def generate_embedding(self, text: str) -> list[float]:
        tokens = re.findall(r"\w+", text.lower())
        counts = Counter(tokens)
        vocab = sorted(counts)
        if not vocab:
            return [0.0]
        vector = [float(counts[token]) for token in vocab]
        magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / magnitude for value in vector]
