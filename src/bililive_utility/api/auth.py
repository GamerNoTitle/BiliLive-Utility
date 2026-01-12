from fastapi import APIRouter, Query, HTTPException
from ..bilibili import api as bilibili_api
from ..utils.qr import generate_qr_code_image

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/getcode", summary="获取登录二维码")
async def get_login_qr_code():
    try:
        qr_data = await bilibili_api.generate_qr_code()
        return {"success": True, "data": qr_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/poll", summary="轮询登录状态")
async def poll_login_status(qrcode_key: str = Query(...)):
    if not qrcode_key:
        raise HTTPException(status_code=400, detail="qrcode_key 不能为空")
    try:
        poll_data = await bilibili_api.poll_qr_status(qrcode_key)
        return {"success": True, "data": poll_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/getqr", summary="获取二维码图片")
async def get_qr_code_image(link: str = Query(...)):
    try:
        qr_image = generate_qr_code_image(link)
        return {"success": True, "data": qr_image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check_login", summary="检查登录状态")
async def check_login_status():
    is_logged_in = await bilibili_api.check_login_status()
    if is_logged_in:
        return {"success": True}
    return {"success": False}


@router.get("/credentials", summary="获取凭据信息，包括房间号和 Cookies")
async def get_credentials():
    try:
        cookies = await bilibili_api.get_cookies()
        room_id = await bilibili_api.get_room_id()
        return {"success": True, "data": {"cookies": cookies, "room_id": room_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/logout", summary="退出登录")
async def logout():
    try:
        await bilibili_api.logout()
        return {"success": True, "data": {"message": "已退出登录"}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))