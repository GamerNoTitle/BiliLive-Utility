from fastapi import APIRouter, Header, HTTPException
from ..bilibili import api as bilibili_api
from .models import startLiveBody

router = APIRouter(prefix="/api/live", tags=["Live Control"])


@router.post("/start", summary="开播")
async def start_live_endpoint(body: startLiveBody):
    try:
        live_data = await bilibili_api.start_live(body.area)
        return {"success": True, "data": live_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开播失败: {e}")


@router.post("/stop", summary="停播")
async def stop_live_endpoint():
    try:
        await bilibili_api.stop_live()
        return {"success": True, "data": {"message": "停播成功"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停播失败: {e}")
