import httpx
import platformdirs
import pickle
import atexit
import logging
from typing import Dict, Optional
from ..context.path import SESSION_PATH

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
    """从缓存加载 Cookies 字典。"""
    if not SESSION_PATH.exists():
        return None
    
    log.info(f"正在从缓存加载 Cookies: {SESSION_PATH}")
    try:
        with open(SESSION_PATH, "rb") as f:
            cookies = pickle.load(f)
            if isinstance(cookies, dict):
                log.info("Cookies 加载成功。")
                return cookies
            log.warning("缓存文件格式不正确，将忽略。")
            return None
    except (pickle.UnpicklingError, EOFError) as e:
        log.warning(f"加载 Cookies 失败 (文件可能已损坏): {e}。将创建新的会话。")
        # 删除损坏的文件
        SESSION_PATH.unlink()
        return None
    except Exception as e:
        log.error(f"加载 Cookies 时发生未知错误: {e}")
        return None

def save_cookies(client: httpx.AsyncClient):
    """在程序退出时，将当前会话的 Cookies 保存到缓存文件。"""
    log.info(f"正在将会话 Cookies 保存到: {SESSION_PATH}")
    try:
        # 只提取并保存 cookies 字典
        cookies_dict = dict(client.cookies)
        with open(SESSION_PATH, "wb") as f:
            pickle.dump(cookies_dict, f)
        log.info("Cookies 保存成功。")
    except Exception as e:
        log.error(f"保存 Cookies 失败: {e}")

# --- 全局会话客户端 ---
# 创建一个新的客户端，并使用加载的 cookies
bili_client = httpx.AsyncClient(
    headers=HEADERS,
    cookies=load_cookies(),
    timeout=15.0
)

# 退出时保存 Cookies
atexit.register(save_cookies, bili_client)