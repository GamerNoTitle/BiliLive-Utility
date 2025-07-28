from fastapi import APIRouter, Header, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field

from ..bilibili import api as bilibili_api

router = APIRouter(prefix="/api/room", tags=["Room Management"])


class AreaUpdate(BaseModel):
    parent_id: int = Field(alias="area")
    id: int = Field(alias="sub_area")


class RoomInfoUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    area: Optional[AreaUpdate] = None


@router.get("/areas", summary="获取所有直播分区")
async def get_areas():
    try:
        area_data = await bilibili_api.get_area_list()
        return {"success": True, "data": area_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分区列表失败: {e}")


@router.get("/info", summary="获取直播间信息")
async def get_room_info_endpoint():
    try:
        info = await bilibili_api.get_room_info()
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取直播间信息失败: {e}")


@router.post("/info", summary="更新直播间信息")
async def update_room_info_endpoint(
    update_data: RoomInfoUpdate,
):
    updates = {}
    if update_data.title is not None:
        updates["title"] = update_data.title
    if update_data.tags is not None:
        updates["tags"] = update_data.tags
    if update_data.area is not None:
        updates["area"] = update_data.area.id

    if not updates:
        raise HTTPException(status_code=400, detail="没有提供任何需要更新的信息")

    try:
        await bilibili_api.update_room_info(updates)
        return {"success": True, "data": {"message": "直播间信息更新成功"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {e}")
