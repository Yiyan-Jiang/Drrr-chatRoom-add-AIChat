import os
from pathlib import Path
import subprocess
import sys
import unittest


class MySQLOnlyRuntimeTest(unittest.TestCase):
    def test_app_starts_without_ai_dependencies_and_ai_routes_are_unavailable(self):
        script = """
import asyncio
import builtins
from unittest.mock import AsyncMock, patch

original_import = builtins.__import__
def import_without_ai(name, *args, **kwargs):
    if name.split('.')[0] in {'ai', 'asyncpg', 'openai'}:
        raise ModuleNotFoundError(f'Removed dependency imported: {name}')
    return original_import(name, *args, **kwargs)
builtins.__import__ = import_without_ai

import httpx
from app_factory import create_app
from main import socketio_app

async def verify():
    app = create_app()
    normal_init = AsyncMock()
    with patch('lifespan.init_db', normal_init):
        async with app.router.lifespan_context(app):
            normal_init.assert_awaited_once()
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=socketio_app),
                base_url='http://test',
            ) as client:
                schema = (await client.get('/openapi.json')).json()
                assert '/api/auth/login' in schema['paths']
                assert '/api/rooms/' in schema['paths']
                assert '/api/private-messages/{friend_id}' in schema['paths']
                assert not any(path.startswith('/api/ai') for path in schema['paths'])
                for path in ('/api/ai/chat', '/api/ai/turn', '/api/ai/turn/stream'):
                    assert (await client.post(path, json={})).status_code == 404
                assert (await client.get('/api/ai/turn/history')).status_code == 404

asyncio.run(verify())
"""
        env = os.environ.copy()
        for key in list(env):
            if key.startswith(('AI_', 'AGENT_CORE_', 'DEEPSEEK_', 'OPENAI_')):
                env.pop(key)
        env['DATABASE_URL'] = 'mysql+aiomysql://user:pass@localhost:3306/chat_rooms'
        result = subprocess.run(
            [sys.executable, '-c', script],
            cwd=Path(__file__).resolve().parents[1],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
