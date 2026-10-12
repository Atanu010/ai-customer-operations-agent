from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.evaluation_service import EvaluationService
from scripts.seed_database import seed_database


async def main() -> None:
    await seed_database()
    result = await EvaluationService().run_suite()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
