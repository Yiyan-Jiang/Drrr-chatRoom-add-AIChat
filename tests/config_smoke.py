"""通过真实 ASGI 启动入口验证非法配置会明确阻止服务启动。"""

import os
import secrets
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """使用真实启动入口核对非法密钥和令牌有效期在连接数据库前被拒绝。"""
    backend = Path(__file__).resolve().parents[1] / "backend"
    jwt_secret = secrets.token_urlsafe(48)
    gate_secret = secrets.token_urlsafe(48)
    cases = []
    for name in ("CHAT_JWT_SECRET", "CHAT_GATE_COOKIE_SECRET"):
        for label, value in (
            ("缺失", ""),
            ("短于32字节", "s" * 31),
            ("UTF8短于32字节", "密" * 10),
            ("旧默认", "dev-change-me-in-production"),
            ("旧示例占位", "change-me-to-a-random-secret-with-at-least-32-bytes"),
        ):
            cases.append((f"{name} {label}", {name: value}, name))
    cases.append(
        (
            "签名密钥相同",
            {"CHAT_GATE_COOKIE_SECRET": jwt_secret},
            "CHAT_GATE_COOKIE_SECRET",
        )
    )
    for value in ("not-a-number", "0", "604801"):
        cases.append(
            (
                f"令牌有效期 {value}",
                {"CHAT_ACCESS_TOKEN_EXPIRE_SECONDS": value},
                "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS",
            )
        )
    for label, overrides, diagnostic in cases:
        # Given（前置）：使用仅指向本机的数据库地址，不接入现有业务库。
        environment = {
            **os.environ,
            "DATABASE_URL": "mysql+aiomysql://smoke:smoke@127.0.0.1:9/config_smoke",
            "CHAT_JWT_SECRET": jwt_secret,
            "CHAT_GATE_COOKIE_SECRET": gate_secret,
            "CHAT_GATE_PASSWORD": "config-smoke-local-password",
            "CHAT_ACCESS_TOKEN_EXPIRE_SECONDS": "3600",
            **overrides,
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
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        # Then（结果）：服务明确指出非法配置，且在尝试连接数据库前退出。
        output = result.stdout + result.stderr
        assert result.returncode != 0, f"非法配置 {label} 未阻止服务启动"
        assert diagnostic in output, f"非法配置 {label} 未产生配置诊断：\n{output}"
        assert "Can't connect to MySQL server" not in output, (
            "非法配置未在数据库连接前被拒绝"
        )
        print(f"PASS 非法配置拒绝启动：{label}")


if __name__ == "__main__":
    main()
