import hashlib
import urllib.parse
from typing import Dict, Any

# --- 常量 ---
APPKEY = "aae92bc66f3edfab"
APPSEC = "af125a0d5279fd576c1b4418a3e8276d"
QR_CODE_GENERATE_URL = (
    "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
)
QR_CODE_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"


def get_sign(params: Dict[str, Any], appkey: str = APPKEY, appsec: str = APPSEC) -> str:
    """为请求参数进行 APP 签名"""
    params["appkey"] = appkey
    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    return hashlib.md5((query + appsec).encode()).hexdigest()


def parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    """将 Cookie 字符串解析为字典"""
    cookie_dict = {}
    if not cookie_string:
        return cookie_dict
    for pair in cookie_string.split(";"):
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookie_dict[key.strip()] = value.strip()
    return cookie_dict


def cookie_dict_to_string(cookies: Dict[str, str]) -> str:
    """将 Cookie 字典转换为字符串"""
    return "; ".join([f"{k}={v}" for k, v in cookies.items()])
