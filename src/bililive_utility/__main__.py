import uvicorn
import os
import webview
import threading
import socket
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from .api import auth, room, live, app_info
from .utils.version import VERSION
from .context.path import get_resource_path

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
static_path = os.path.join(get_resource_path(), "static")
print(f"Static files path: {static_path}")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

# --- 启动函数 ---
def main(debug: bool = False):
    """
    包含了所有的设置和启动逻辑的启动入口函数
    """
    print(f"Running BiliLive-Utility Version: {VERSION}")
    # 临时绑定端口获取可用端口号
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    url = f"http://127.0.0.1:{port}"
    print(url)

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None)
    server = uvicorn.Server(config=config)

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    window_title = "BiliLive Utility"
    webview.settings["ALLOW_DOWNLOADS"] = True
    webview.settings["ALLOW_FILE_URLS"] = True
    webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True
    webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = True
    print(webview.settings)
    webview.create_window(
        window_title,
        url,
        width=1280,
        height=720,
        resizable=True,
        frameless=False,
    )

    webview.start(icon="static/icon.ico", debug=debug)


if __name__ == "__main__":
    main()
