"""提供 Uvicorn 使用的统一 ASGI 入口。"""

from app_factory import socketio_app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:socketio_app", host="127.0.0.1", port=8000, reload=True)
