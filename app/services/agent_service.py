from __future__ import annotations

from app.agents.customer_agent import CustomerOperationsAgent
from app.db.database import async_session_factory


class AgentService:
    def __init__(self):
        self.agent = CustomerOperationsAgent()

    async def process_query(self, message: str, customer_id: int | None = None) -> dict:
        async with async_session_factory() as session:
            agent = CustomerOperationsAgent(session=session)
            return await agent.handle_request(message, customer_id=customer_id)
