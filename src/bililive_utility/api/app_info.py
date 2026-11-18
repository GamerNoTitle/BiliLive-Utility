import os
import re
import webbrowser
import httpx
from fastapi import APIRouter, Header, Query, HTTPException
from typing import Optional
from ..bilibili import api as bilibili_api
from ..bilibili.session import bili_client
from ..context.path import CACHE_PATH, LEGACY_CACHE_PATH
from ..utils.version import VERSION

GITHUB_REPO = "GamerNoTitle/BiliLive-Utility"
RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases"

router = APIRouter(prefix="/api/application", tags=["Application"])


def _parse_version(v: str) -> tuple[int, ...] | None:
    """解析版本号"""
    m = re.match(r"^v?(\d+(?:\.\d+)*)", v)
    if m:
        return tuple(int(x) for x in m.group(1).split("."))
    return None


def _has_update(current: str, remote: str) -> bool:
    """比较版本号"""
    cur = _parse_version(current)
    rem = _parse_version(remote)
    if cur is None:
        return True
    if rem is None:
        return False
    return rem > cur


def _disclaimer_accepted() -> bool:
    """免责声明是否已被同意：优先新路径，兼容旧版本的 v2 目录（只读，不迁移、不删除）"""
    for path in (CACHE_PATH / "access", LEGACY_CACHE_PATH / "access"):
        if path.exists():
            return True
    return False


@router.get("/info", summary="获取应用及账户状态")
async def get_application_info():
    app_info = {
        "first_access": _disclaimer_accepted(),
        "version": VERSION.version,
        "build": VERSION.build,
    }

    try:
        room_info = await bilibili_api.get_room_info()
        account_info = {
            "is_live": room_info.get("live_status") == 1,
            "room_id": room_info.get("room_id"),
        }
        return {
            "success": True,
            "data": {"application": app_info, "account": account_info},
        }
    except Exception:
        return {
            "success": True,
            "data": {
                "application": app_info,
                "account": {"is_live": False, "room_id": None},
            },
        }


@router.get("/first_access", summary="更改首次访问状态")
async def set_first_access():
    app_info = {"first_access": _disclaimer_accepted()}
    if not app_info["first_access"]:
        # 缓存目录按需创建，不在程序启动时预先建目录
        (CACHE_PATH / "access").parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH / "access", "w") as f:
            pass
        return {"success": True, "data": {"first_access": True}}


# 清除缓存时需要一并删除的本机凭据与状态文件
CACHE_FILE_NAMES = ("session", "room_id")
# 新路径优先；旧版本写入的 v2 目录也必须一起清理，否则清理后程序仍会从旧路径读回凭据
CACHE_LOCATIONS = (CACHE_PATH, LEGACY_CACHE_PATH)


@router.post("/clear_cache", summary="清除本地缓存")
async def clear_cache():
    """清除本地保存的会话缓存和直播间号缓存

    这是一次由用户在界面上显式确认的操作，只删除程序自己写入的凭据与状态文件；
    不会删除任何目录，也不会碰缓存目录里的其他内容。
    """
    cleared = []
    for location in CACHE_LOCATIONS:
        for name in CACHE_FILE_NAMES:
            path = location / name
            try:
                if path.exists():
                    path.unlink()
                    cleared.append(str(path))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"清除 {path} 失败: {e}")

    # 同步清空进程内的凭据与内存缓存，避免清理后仍带着旧状态继续请求
    bili_client.cookies.clear()
    bilibili_api.invalidate_room_id_cache()

    return {
        "success": True,
        "data": {
            "cleared": cleared,
            "message": "缓存已清除，请重启应用后重新扫码登录",
        },
    }


@router.get("/disagree", summary="用户不同意免责声明")
async def disagree_disclaimer_handler():
    os._exit(0)


@router.get("/exit", summary="退出应用")
async def exit_application():
    os._exit(0)


@router.get("/releases", summary="检查更新")
async def check_releases(prerelease: bool = Query(False)):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if prerelease:
                resp = await client.get(
                    GITHUB_API,
                    headers={"Accept": "application/vnd.github.v3+json"},
                    params={"per_page": 10},
                )
                if resp.status_code != 200:
                    return {
                        "success": False,
                        "data": {"error": f"GitHub API 返回 {resp.status_code}"},
                    }
                releases = resp.json()
                release = next((r for r in releases if r.get("prerelease")), None)
            else:
                resp = await client.get(
                    f"{GITHUB_API}/latest",
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 404:
                    return {
                        "success": True,
                        "data": {
                            "has_update": False,
                            "current_version": VERSION.version,
                        },
                    }
                if resp.status_code != 200:
                    return {
                        "success": False,
                        "data": {"error": f"GitHub API 返回 {resp.status_code}"},
                    }
                release = resp.json()

            if not release:
                return {
                    "success": True,
                    "data": {"has_update": False, "current_version": VERSION.version},
                }

            tag = release.get("tag_name", "")
            return {
                "success": True,
                "data": {
                    "has_update": _has_update(VERSION.version, tag),
                    "current_version": VERSION.version,
                    "version": tag,
                    "url": release.get("html_url", ""),
                    "body": release.get("body", ""),
                    "published_at": release.get("published_at", ""),
                    "prerelease": release.get("prerelease", False),
                },
            }
    except Exception as e:
        return {"success": False, "data": {"error": str(e)}}


@router.get("/update", summary="打开浏览器前往更新页面")
async def open_update_page():
    try:
        webbrowser.open(RELEASES_URL)
        return {"success": True, "data": {"message": "已打开浏览器"}}
    except Exception as e:
        return {"success": False, "data": {"error": str(e)}}
