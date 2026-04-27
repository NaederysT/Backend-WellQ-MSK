"""
Apply the WellQ MongoDB model to the configured database.

Run from the repo root:
    python -m app.scripts.setup_mongodb
"""

import asyncio

from app.db.mongodb import close_mongodb, get_mongo_db, init_mongodb
from app.db.mongo_schema import ensure_mongo_schema


async def main() -> None:
    init_mongodb()
    try:
        await ensure_mongo_schema(get_mongo_db())
    finally:
        await close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())
