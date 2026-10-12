from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import TOOL_REGISTRY
from app.llm.base import ToolCall
from app.llm.provider import LLMProviderFactory

logger = logging.getLogger("ai_customer_ops")


class CustomerOperationsAgent:
    def __init__(self, session: AsyncSession | None = None):
        self.session = session
        self.llm = LLMProviderFactory.create()

    @staticmethod
    def _tool_definitions() -> list[dict[str, Any]]:
        return [
            {"name": "get_order_status", "description": "Check the current status of a specific order.", "arguments": {"order_id": {"type": "integer"}}},
            {"name": "get_order_details", "description": "Retrieve detailed order information for a specific order.", "arguments": {"order_id": {"type": "integer"}}},
            {"name": "get_customer_orders", "description": "Return all orders for a customer account.", "arguments": {"customer_id": {"type": "integer"}}},
            {"name": "search_knowledge_base", "description": "Search the knowledge base for product and policy answers.", "arguments": {"query": {"type": "string"}}},
            {"name": "create_support_interaction", "description": "Persist a support interaction for auditing and follow-up.", "arguments": {"customer_id": {"type": "integer"}, "request_text": {"type": "string"}, "detected_intent": {"type": "string"}, "tool_used": {"type": "string"}, "response": {"type": "string"}, "success": {"type": "boolean"}, "latency_ms": {"type": "integer"}}},
        ]

    def _validate_tool_call(self, tool_name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
        if tool_name not in TOOL_REGISTRY:
            raise ValueError(f"Tool '{tool_name}' is not allowed.")
        payload = dict(arguments or {})

        if tool_name in {"get_order_status", "get_order_details"}:
            order_id = payload.get("order_id")
            if order_id is None:
                raise ValueError(f"Tool '{tool_name}' requires an order_id.")
            payload["order_id"] = int(order_id)
            if payload["order_id"] <= 0:
                raise ValueError("order_id must be a positive integer.")
            return payload

        if tool_name == "get_customer_orders":
            customer_id = payload.get("customer_id")
            if customer_id is None:
                raise ValueError("Tool 'get_customer_orders' requires a customer_id.")
            payload["customer_id"] = int(customer_id)
            if payload["customer_id"] <= 0:
                raise ValueError("customer_id must be a positive integer.")
            return payload

        if tool_name == "search_knowledge_base":
            query = payload.get("query")
            if not isinstance(query, str) or len(query.strip()) < 2:
                raise ValueError("search_knowledge_base requires a meaningful query string.")
            payload["query"] = query.strip()
            return payload

        if tool_name == "create_support_interaction":
            required = ["customer_id", "request_text", "detected_intent", "response", "success", "latency_ms"]
            for name in required:
                if name not in payload:
                    raise ValueError(f"Tool '{tool_name}' requires '{name}'.")
            payload["customer_id"] = int(payload["customer_id"])
            payload["latency_ms"] = int(payload["latency_ms"])
            if payload["customer_id"] <= 0:
                raise ValueError("customer_id must be a positive integer.")
            if not isinstance(payload["request_text"], str) or not payload["request_text"].strip():
                raise ValueError("request_text cannot be empty.")
            if not isinstance(payload["response"], str):
                raise ValueError("response must be a string.")
            return payload

        raise ValueError(f"Tool '{tool_name}' is not supported by the validator.")

    async def classify_request(self, message: str) -> dict[str, Any]:
        classification = await self.llm.classify_intent(message)
        logger.info("Detected intent=%s confidence=%.2f", classification.intent, classification.confidence)
        return {
            "intent": classification.intent,
            "order_id": classification.order_id,
            "confidence": classification.confidence,
            "requires_tool": classification.requires_tool,
        }

    async def execute_tool(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        validated = self._validate_tool_call(tool_name, kwargs)
        tool_fn = TOOL_REGISTRY[tool_name]
        if self.session is None:
            raise RuntimeError("Database session is required for tool execution.")
        return await tool_fn(self.session, **validated)

    async def handle_request(self, message: str, customer_id: int | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        classification = await self.classify_request(message)
        selected_tool_calls: list[ToolCall] = await self.llm.select_tools(message, self._tool_definitions())
        tool_name = None
        tool_result = None

        if selected_tool_calls:
            selected = selected_tool_calls[0]
            tool_name = selected.tool_name
            try:
                validated_args = self._validate_tool_call(tool_name, selected.arguments)
                tool_result = await self.execute_tool(tool_name, **validated_args)
            except ValueError as exc:
                logger.warning("Rejected invalid tool call %s: %s", tool_name, exc)
                tool_result = {"status": "error", "tool_name": tool_name, "message": str(exc)}

        if tool_result is None and classification["intent"] == "GENERAL_SUPPORT":
            tool_name = "search_knowledge_base"
            tool_result = await self.execute_tool(tool_name, query=message)
        elif tool_result is None and classification["intent"] == "RETURN_POLICY":
            tool_name = "search_knowledge_base"
            tool_result = await self.execute_tool(tool_name, query="return policy refund cancellation")
        elif tool_result is None and customer_id and classification["intent"] in {"ORDER_DETAILS", "UNKNOWN"}:
            tool_name = "get_customer_orders"
            tool_result = await self.execute_tool(tool_name, customer_id=customer_id)

        llm_output = await self.llm.generate_response(
            message=message,
            intent=classification["intent"],
            tool_result={**(tool_result or {}), "tool_name": tool_name, "order_id": classification["order_id"]},
        )

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info("Agent request processed in %d ms", latency_ms)

        response = {
            "intent": classification["intent"],
            "answer": llm_output.get("answer", "I’m unable to answer that request right now."),
            "actions_taken": [tool_name] if tool_name else [],
            "order_id": classification["order_id"],
            "confidence": classification["confidence"],
            "requires_human": classification["intent"] == "UNKNOWN",
            "requires_tool": classification["requires_tool"],
            "tool_used": tool_name,
        }
        return response
