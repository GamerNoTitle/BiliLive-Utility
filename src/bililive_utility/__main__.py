import uvicorn
import os
import webview
import threading
import socket
import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from pathlib import Path

from .api import auth, room, live, app_info
from .utils.version import VERSION

# --- 应用初始化 ---
app = FastAPI(
    title="BiliLive Utility",
    version=VERSION.version,
)


# --- 异常处理器 ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": {"error": exc.detail}},
    )


# --- 中间件 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 包含 API 路由 ---
app.include_router(auth.router)
app.include_router(room.router)
app.include_router(live.router)
app.include_router(app_info.router)

# --- 静态文件服务 ---
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    print(f"警告: 未找到静态文件目录 {static_path}，前端将不可用。")


# --- 启动函数 ---
def run_server(server: uvicorn.Server, sockets: list):
    """
    封装，用于在线程中启动服务器。
    """
    with contextlib.suppress(KeyboardInterrupt):
        server.run(sockets=sockets)


def main():
    """
    包含了所有的设置和启动逻辑的启动入口函数
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock4:
        sock4.bind(("127.0.0.1", 0))
        sock4.listen()
        port = sock4.getsockname()[1]

        try:
            sock6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock6.bind(("::1", port))
            sock6.listen()
            sockets = [sock4, sock6]
        except OSError:
            sockets = [sock4]

        url = f"http://127.0.0.1:{port}"
        print(url)

        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None)
        server = uvicorn.Server(config=config)

        server_thread = threading.Thread(target=run_server, args=(server, sockets))
        server_thread.daemon = True
        server_thread.start()

        window_title = "BiliLive Utility"
        webview.create_window(
            window_title,
            url,
            width=1280,
            height=720,
        )

        webview.start()


if __name__ == "__main__":
    main()
