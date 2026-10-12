import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import get_order_status
from app.db.database import async_session_factory


@pytest.mark.asyncio
async def test_get_order_status_tool() -> None:
    async with async_session_factory() as session:
        result = await get_order_status(session, 1001)
        assert result["status"] == "ok"
        assert result["order"]["status"] == "in_transit"


@pytest.mark.asyncio
async def test_invalid_tool_input() -> None:
    async with async_session_factory() as session:
        with pytest.raises(ValueError):
            await get_order_status(session, 0)
