import os
from fastapi import APIRouter, Header
from typing import Optional
from ..bilibili import api as bilibili_api
from ..context.path import CACHE_PATH
from ..utils.version import VERSION

router = APIRouter(prefix="/api/application", tags=["Application"])

@router.get("/info", summary="获取应用及账户状态")
async def get_application_info(
    x_cookies: Optional[str] = Header(None),
    x_room_id: Optional[str] = Header(None),
):
    app_info = {"first_access": os.path.exists(CACHE_PATH / "access"), "version": VERSION.version}
    
    if not x_cookies or not x_room_id:
        return {"success": True, "data": {
            "application": app_info, "account": {"is_live": False, "room_id": None}
        }}

    try:
        room_info = await bilibili_api.get_room_info(x_room_id, x_cookies)
        account_info = {"is_live": room_info.get("live_status") == 1, "room_id": x_room_id}
        return {"success": True, "data": {"application": app_info, "account": account_info}}
    except Exception:
        return {"success": True, "data": {
            "application": app_info, "account": {"is_live": False, "room_id": x_room_id}
        }}
        
@router.get("/first_access", summary="更改首次访问状态")
async def set_first_access():
    app_info = {"first_access": os.path.exists(CACHE_PATH / "access")}
    if not app_info["first_access"]:
        # 创建一个空文件来标记首次访问
        with open(CACHE_PATH / "access", "w") as f:
            pass
        return {"success": True, "data": {"first_access": True}}