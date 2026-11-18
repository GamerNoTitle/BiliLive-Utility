import httpx
import platformdirs
import json
import atexit
import logging
from typing import Dict, Optional

from ..context.path import SESSION_PATH, LEGACY_CACHE_PATH
from ..utils.crypto import encrypt_data, decrypt_data

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# --- 通用请求头 ---
HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://link.bilibili.com",
    "Referer": "https://link.bilibili.com/p/center/index",
}

def load_cookies() -> Optional[Dict[str, str]]:
    """从缓存加载 Cookies 字典"""
    session_path = SESSION_PATH
    if not session_path.exists() and (LEGACY_CACHE_PATH / "session").exists():
        # 只读回退：老用户的凭据还在旧版本的 v2 目录里，读一次即可继续登录状态
        session_path = LEGACY_CACHE_PATH / "session"

    if not session_path.exists():
        return None

    log.info(f"正在从缓存加载 Cookies: {session_path}")
    try:
        with open(session_path, "r") as f:
            encrypted = f.read()
        json_str = decrypt_data(encrypted)
        cookies = json.loads(json_str)
        if isinstance(cookies, dict):
            log.info("Cookies 加载成功。")
            return cookies
        log.warning("缓存文件格式不正确")
        return None
    except Exception as e:
        # 解密失败时保留原文件：是否清理缓存由用户在界面上自行决定，程序不替用户删除数据
        log.warning(
            f"加载 Cookies 失败: {e}"
        )
        return None

def save_cookies(client: httpx.AsyncClient):
    """在程序退出时，将当前会话的 Cookies 加密后保存到缓存文件。"""
    log.info(f"正在将会话 Cookies 保存到: {SESSION_PATH}")
    try:
        cookies_dict = dict(client.cookies)
        encrypted = encrypt_data(json.dumps(cookies_dict))
        # 缓存目录按需创建，不在程序启动时预先建目录
        SESSION_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SESSION_PATH, "w") as f:
            f.write(encrypted)
        log.info("Cookies 保存成功")
    except Exception as e:
        log.error(f"保存 Cookies 失败: {e}")

bili_client = httpx.AsyncClient(
    headers=HEADERS,
    cookies=load_cookies(),
    timeout=15.0
)

atexit.register(save_cookies, bili_client)