import os
import re
import webbrowser
import httpx
from fastapi import APIRouter, Header, Query
from typing import Optional
from ..bilibili import api as bilibili_api
from ..context.path import CACHE_PATH
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


@router.get("/info", summary="获取应用及账户状态")
async def get_application_info():
    app_info = {
        "first_access": os.path.exists(CACHE_PATH / "access"),
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
    app_info = {"first_access": os.path.exists(CACHE_PATH / "access")}
    if not app_info["first_access"]:
        with open(CACHE_PATH / "access", "w") as f:
            pass
        return {"success": True, "data": {"first_access": True}}


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
