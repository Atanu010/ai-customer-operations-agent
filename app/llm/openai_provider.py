from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.llm.base import BaseLLMProvider, IntentClassification, ToolCall


class OpenAICompatibleLLMProvider(BaseLLMProvider):
    def __init__(self, client: OpenAI | None = None, model: str | None = None) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.openai_model

    @staticmethod
    def _parse_json(content: str | None) -> dict[str, Any]:
        if not content:
            raise ValueError("Empty response from OpenAI-compatible provider.")
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError("The model returned invalid JSON.") from exc
        if not isinstance(data, dict):
            raise ValueError("The model returned an unexpected JSON payload.")
        return data

    async def classify_intent(self, message: str) -> IntentClassification:
        system_prompt = (
            "You are a customer operations classifier. Return compact JSON with keys: "
            "intent, order_id, confidence, requires_tool. Valid intents are ORDER_STATUS, "
            "ORDER_DETAILS, DELIVERY_DELAY, RETURN_POLICY, GENERAL_SUPPORT, UNKNOWN."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        )
        payload = self._parse_json(response.choices[0].message.content)
        return IntentClassification(**payload)

    async def select_tools(self, message: str, tools: list[dict[str, Any]] | None = None) -> list[ToolCall]:
        tool_descriptions = tools or [
            {"name": "get_order_status", "description": "Check the current status of a specific order."},
            {"name": "get_order_details", "description": "Retrieve detailed order information."},
            {"name": "get_customer_orders", "description": "Return all orders for a customer."},
            {"name": "search_knowledge_base", "description": "Search the support knowledge base."},
            {"name": "create_support_interaction", "description": "Persist a support interaction."},
        ]
        system_prompt = (
            "Select the most relevant registered tool for the user request. "
            "Return JSON of the form: {\"tool_calls\": [{\"tool_name\": \"tool_name\", \"arguments\": { ... } }]}. "
            "Use at most one tool when appropriate. If no tool is required, return an empty list."
        )
        tool_payload = json.dumps(tool_descriptions)
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": f"Available tools: {tool_payload}\n{system_prompt}"},
                {"role": "user", "content": message},
            ],
        )
        payload = self._parse_json(response.choices[0].message.content)
        tool_calls = payload.get("tool_calls") or payload.get("tools") or []
        normalized: list[ToolCall] = []
        for item in tool_calls:
            if isinstance(item, dict):
                name = item.get("tool_name") or item.get("name")
                args = item.get("arguments") or item.get("args") or {}
                if name:
                    normalized.append(ToolCall(tool_name=str(name), arguments=args if isinstance(args, dict) else {}))
        return normalized

    async def generate_response(self, *, message: str, intent: str, tool_result: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = tool_result or {}
        system_prompt = (
            "You are a customer operations assistant. Return compact JSON with keys: "
            "answer, intent, confidence, requires_human, requires_tool, tool_used, actions_taken."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Intent: {intent}\nUser message: {message}\nTool result: {json.dumps(payload, default=str)}"},
            ],
        )
        result = self._parse_json(response.choices[0].message.content)
        result.setdefault("intent", intent)
        result.setdefault("confidence", 0.9)
        result.setdefault("requires_human", False)
        result.setdefault("requires_tool", bool(payload.get("tool_name")))
        result.setdefault("tool_used", payload.get("tool_name"))
        result.setdefault("actions_taken", [payload.get("tool_name")] if payload.get("tool_name") else [])
        return result

    async def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0]
        response = self.client.embeddings.create(model=settings.openai_embedding_model, input=text)
        return list(response.data[0].embedding)
