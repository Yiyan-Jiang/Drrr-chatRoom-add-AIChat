import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.parametrize("failure", [None, "startup", "request"])
def test_lifespan_releases_database_pool_on_exit(failure):
    os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")
    from lifespan import lifespan

    async def scenario():
        initialize = AsyncMock()
        engine = SimpleNamespace(dispose=AsyncMock())
        if failure == "startup":
            initialize.side_effect = RuntimeError("startup failed")
        with patch("lifespan.init_db", initialize), patch("lifespan.engine", engine, create=True):
            async def run():
                async with lifespan(None):
                    engine.dispose.assert_not_awaited()
                    if failure == "request":
                        raise RuntimeError("request failed")

            if failure:
                with pytest.raises(RuntimeError, match=f"{failure} failed"):
                    await run()
            else:
                await run()
        initialize.assert_awaited_once()
        engine.dispose.assert_awaited_once()

    asyncio.run(scenario())
