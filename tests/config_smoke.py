"""通过真实 ASGI 启动入口验证非法配置会明确阻止服务启动。"""

import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    """分别以非法令牌有效期启动后端，核对退出状态与配置诊断。"""
    backend = Path(__file__).resolve().parents[1] / "backend"
    for value in ("not-a-number", "0", "604801"):
        # Given（前置）：使用仅指向本机的数据库地址，不接入现有业务库。
        environment = {
            **os.environ,
            "DATABASE_URL": "mysql+aiomysql://smoke:smoke@127.0.0.1:9/config_smoke",
            "CHAT_JWT_SECRET": "config-smoke-local-secret",
            "CHAT_GATE_COOKIE_SECRET": "config-smoke-local-gate-secret",
            "CHAT_GATE_PASSWORD": "config-smoke-local-password",
            "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS": value,
        }

        # When（操作）：通过 Uvicorn 的真实 ASGI 启动入口触发生命周期。
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main:socketio_app",
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--lifespan",
                "on",
            ],
            cwd=backend,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        # Then（结果）：服务明确指出非法配置，且在尝试连接数据库前退出。
        output = result.stdout + result.stderr
        assert result.returncode != 0, f"非法配置 {value!r} 未阻止服务启动"
        assert "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS" in output, (
            f"非法配置 {value!r} 未产生配置诊断：\n{output}"
        )
        assert "Can't connect to MySQL server" not in output, (
            "非法配置未在数据库连接前被拒绝"
        )
        print(f"PASS 非法令牌有效期拒绝启动：{value}")


if __name__ == "__main__":
    main()
