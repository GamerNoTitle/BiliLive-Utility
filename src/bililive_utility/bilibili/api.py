import time
import asyncio
from typing import Dict, Any, List, Tuple

from .session import bili_client, save_cookies
from .core import (
    get_sign,
    parse_cookie_string,
    cookie_dict_to_string,
    QR_CODE_GENERATE_URL,
    QR_CODE_POLL_URL,
    APPKEY,
    APPSEC,
)
from ..context.path import CACHE_PATH


async def generate_qr_code() -> Dict[str, Any]:
    """生成登录二维码"""
    response = await bili_client.get(QR_CODE_GENERATE_URL)
    response.raise_for_status()
    data = response.json()
    if data.get("code") == 0:
        return data["data"]
    raise Exception(f"生成二维码失败: {data.get('message', '未知错误')}")


async def poll_qr_status(qrcode_key: str) -> Dict[str, Any]:
    """轮询二维码扫描状态"""
    params = {"qrcode_key": qrcode_key}
    response = await bili_client.get(QR_CODE_POLL_URL, params=params)
    response.raise_for_status()
    data = response.json()

    status_data = data.get("data", {})
    status_code = status_data.get("code", -1)
    result = {"code": status_code, "message": status_data.get("message")}

    if status_code == 0:  # 登录成功
        # 会话中的 cookie 已经自动更新
        cookies_dict = dict(bili_client.cookies)
        dede_user_id = cookies_dict.get("DedeUserID")
        if not dede_user_id:
            raise Exception("登录成功，但无法从 Cookie 中提取 DedeUserID")

        room_id = await get_user_room_id(dede_user_id)

        result["data"] = {
            "cookies": cookie_dict_to_string(cookies_dict),
            "room_id": room_id,
        }

        # 保存 room_id 到本地存储
        with open(CACHE_PATH / "room_id", "w") as f:
            f.write(room_id)
        # 保存一次 session 到本地存储
        save_cookies(bili_client)
    return result


async def get_user_room_id(mid: str) -> str:
    """通过用户 ID 获取直播间 ID"""
    resp = await bili_client.get(
        "https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld",
        params={"mid": mid},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") == 0:
        room_id = data.get("data", {}).get("roomid")
        if room_id:
            return str(room_id)
    raise Exception(f"获取直播间ID失败: {data.get('message', '未能找到直播间')}")


async def get_area_list() -> List[Dict[str, Any]]:
    """获取直播分区列表"""
    response = await bili_client.get(
        "https://api.live.bilibili.com/room/v1/Area/getList"
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") == 0:
        return data.get("data", [])
    raise Exception("获取分区列表失败")


async def get_room_info() -> Dict[str, Any]:
    """获取直播间详细信息"""
    room_id = (CACHE_PATH / "room_id").read_text().strip()
    resp = await bili_client.get(
        "https://api.live.bilibili.com/room/v1/Room/get_info",
        params={"room_id": room_id},
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") == 0:
        rd = data.get("data", {})
        return {
            "title": rd.get("title", ""),
            "tags": rd.get("tags", "").split(","),
            "live_status": rd.get("live_status", 0),
            "area": {"parent_id": rd.get("parent_area_id"), "id": rd.get("area_id")},
        }
    raise Exception(f"获取直播间信息失败: {data.get('message', '未知错误')}")


async def update_room_info(updates: Dict[str, Any]):
    """更新直播间信息 (标题, 标签, 分区)"""
    cookies = bili_client.cookies
    room_id = (CACHE_PATH / "room_id").read_text().strip()
    csrf = cookies.get("bili_jct")
    if not csrf:
        raise ValueError("Cookies 中缺少 'bili_jct'，无法执行操作")

    base_data = {"room_id": room_id, "csrf": csrf, "csrf_token": csrf}

    async def post_update(payload):
        resp = await bili_client.post(
            "https://api.live.bilibili.com/room/v1/Room/update",
            data=payload,
            cookies=cookies,
        )
        resp.raise_for_status()
        json_resp = resp.json()
        if json_resp.get("code") != 0:
            raise Exception(f"更新操作失败: {json_resp.get('message')}")

    if "title" in updates:
        await post_update({**base_data, "title": updates["title"]})
    if "area" in updates:
        await post_update({**base_data, "area_id": updates["area"]})
    if "tags" in updates:
        new_tags = set(tag for tag in updates["tags"] if tag)
        current_info = await get_room_info()
        current_tags = set(tag for tag in current_info.get("tags", []) if tag)

        for tag in current_tags - new_tags:
            await post_update({**base_data, "del_tag": tag})
            await asyncio.sleep(2)
        for tag in new_tags - current_tags:
            await post_update({**base_data, "add_tag": tag})
            await asyncio.sleep(2)


async def start_live(area) -> Dict[str, Any]:
    """开始直播"""
    cookies = bili_client.cookies
    room_id = (CACHE_PATH / "room_id").read_text().strip()
    csrf = cookies.get("bili_jct")
    if not csrf:
        raise ValueError("Cookies 中缺少 'bili_jct'")

    current_info = await get_room_info()
    area_id = current_info.get("area", {}).get("id")
    if not area_id:
        raise Exception("无法获取当前分区ID，无法开播")

    pc_link_version, pc_link_build = await get_pc_link_build()

    data = {
        "room_id": room_id,
        "platform": "pc_link",
        "area_v2": area,
        "csrf_token": csrf,
        "csrf": csrf,
        "ts": int(time.time()),
        "version": pc_link_version,
        "build": pc_link_build,
        "appkey": APPKEY,
    }
    data["sign"] = get_sign(data.copy(), appkey=APPKEY, appsec=APPSEC)

    resp = await bili_client.post(
        "https://api.live.bilibili.com/room/v1/Room/startLive",
        data=data,
    )
    resp.raise_for_status()
    start_resp = resp.json()

    if start_resp.get("code") == 0:
        return start_resp.get("data", {})
    raise Exception(f"{start_resp.get('message', '未知错误')}")


async def stop_live():
    """停止直播"""
    room_id = (CACHE_PATH / "room_id").read_text().strip()
    cookies = bili_client.cookies
    csrf = cookies.get("bili_jct")
    if not csrf:
        raise ValueError("Cookies 中缺少 'bili_jct'")

    data = {"room_id": room_id, "platform": "pc_link", "csrf_token": csrf, "csrf": csrf}

    resp = await bili_client.post(
        "https://api.live.bilibili.com/room/v1/Room/stopLive",
        data=data,
    )
    resp.raise_for_status()
    stop_resp = resp.json()

    if stop_resp.get("code") != 0:
        raise Exception(f"停播失败: {stop_resp.get('message', '未知错误')}")


async def check_login_status():
    # 通过读取 session 后 GET 请求到 https://api.bilibili.com/x/web-interface/nav 查看是否登录
    try:
        response = await bili_client.get("https://api.bilibili.com/x/web-interface/nav")
        response.raise_for_status()
        data = response.json()
        if data.get("data", {}).get("isLogin"):
            return True
        return False
    except Exception as e:
        return False


async def get_cookies():
    """获取当前登录的 Cookies"""
    cookies = bili_client.cookies
    if not cookies:
        raise ValueError("未找到有效的 Cookies")
    return cookie_dict_to_string(dict(cookies))


async def get_room_id():
    """获取当前登录的房间 ID"""
    room_id_path = CACHE_PATH / "room_id"
    if not room_id_path.exists():
        return ""
    return room_id_path.read_text().strip()


async def get_pc_link_build() -> Tuple[str, str]:
    """获取当前 PC 端直播链接的版本和构建号"""
    body = {"appkey": APPKEY, "ts": int(time.time()), "system_version": "2"}
    resp = await bili_client.get(
        f"https://api.live.bilibili.com/xlive/app-blink/v1/liveVersionInfo/getHomePageLiveVersion?system_version=2&appkey={APPKEY}&ts={body['ts']}&sign={get_sign(body, appkey=APPKEY, appsec=APPSEC)}"
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            version = data.get("data", {}).get("curr_version", "7.19.0.1000")
            build = data.get("data", {}).get("build", "1000")
        else:
            version = "7.19.0.1000"
            build = "1000"
    return version, build
