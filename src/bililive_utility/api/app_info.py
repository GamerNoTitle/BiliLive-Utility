import os
from fastapi import APIRouter, Header
from typing import Optional
from ..bilibili import api as bilibili_api
from ..context.path import CACHE_PATH
from ..utils.version import VERSION

router = APIRouter(prefix="/api/application", tags=["Application"])


@router.get("/info", summary="获取应用及账户状态")
async def get_application_info(
):
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
        # 创建一个空文件来标记首次访问
        with open(CACHE_PATH / "access", "w") as f:
            pass
        return {"success": True, "data": {"first_access": True}}


@router.get("/disagree", summary="用户不同意免责声明")
async def disagree_disclaimer_handler():
    """
    用户不同意免责声明时，直接退出程序
    """
    os._exit(0)


@router.get("/exit", summary="退出应用")
async def exit_application():
    os._exit(0)
