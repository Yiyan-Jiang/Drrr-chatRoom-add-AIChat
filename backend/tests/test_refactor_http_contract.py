import json
import os
from pathlib import Path


def test_http_contract_matches_pre_refactor_baseline():
    os.environ.setdefault("DATABASE_URL", "mysql+aiomysql://test:test@localhost:3306/chat_rooms")
    from app_factory import app

    baseline = json.loads(
        (Path(__file__).parent / "fixtures" / "http_contract.json").read_text(encoding="utf-8")
    )
    assert app.openapi() == baseline
