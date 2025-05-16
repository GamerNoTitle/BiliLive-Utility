import flet as ft
import requests
import threading
import qrcode
import io
import base64
import time
from datetime import datetime
from home import save_log_to_file

# B 站登录相关的 API 端点
QR_CODE_GENERATE_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
QR_CODE_POLL_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
TIMEOUT_SECONDS = 180  # 二维码超时时间为 180 秒

def generate_qr_code_image(url):
    """生成二维码图片并返回 base64 数据"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # 添加数据到二维码
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    save_log_to_file(f"生成 URL 二维码：{url}", level="DEBUG")
    # 将图片转为 base64 数据
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    save_log_to_file(f"生成二维码图片成功，base64 数据长度：{len(img_base64)}，图片数据：{img_base64}", level="DEBUG")
    return img_base64

class QRLoginClient:
    def __init__(self, status_text, qr_image, page):
        self.qrcode_key = None
        self.qr_url = None
        self.status_text = status_text
        self.qr_image = qr_image
        self.page = page
        self.is_polling = False
        self.start_time = None

    def generate_qr_code(self):
        """生成二维码"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Referer": "https://passport.bilibili.com/login",
        }
        try:
            response = requests.get(QR_CODE_GENERATE_URL, headers=headers)
            save_log_to_file(f"请求二维码生成接口，状态码：{response.status_code}，回复：{response.text}", level="DEBUG")
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self.qr_url = data.get("data", {}).get("url", "")
                    self.qrcode_key = data.get("data", {}).get("qrcode_key", "")
                    self.start_time = time.time()
                    # 生成二维码图片并更新界面
                    qr_base64 = generate_qr_code_image(self.qr_url)
                    self.qr_image.src_base64 = qr_base64
                    self.status_text.value = "请使用 B 站手机客户端扫码登录"
                    self.page.update()
                    # 开始轮询
                    if not self.is_polling:
                        self.is_polling = True
                        threading.Thread(target=self.poll_qr_status).start()
                    return True
            self.status_text.value = "❌ 生成二维码失败，请重试"
            save_log_to_file(f"生成二维码失败，状态码：{response.status_code}，回复：{response.text}", level="ERROR")
            self.page.update()
            return False
        except Exception as e:
            self.status_text.value = f"❌ 网络错误：{str(e)}"
            save_log_to_file(f"网络错误：{str(e)}", level="ERROR")
            self.page.update()
            return False

    def poll_qr_status(self):
        """轮询二维码扫码状态"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Referer": "https://passport.bilibili.com/login",
        }
        while self.is_polling:
            if time.time() - self.start_time > TIMEOUT_SECONDS:
                self.status_text.value = "❌ 二维码已超时，正在刷新..."
                save_log_to_file("二维码已超时，进行刷新", level="WARNING")
                self.page.update()
                self.is_polling = False
                self.generate_qr_code()
                return

            try:
                response = requests.get(
                    QR_CODE_POLL_URL,
                    params={"qrcode_key": self.qrcode_key},
                    headers=headers
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        status_data = data.get("data", {})
                        status_code = status_data.get("code", -1)
                        status_msg = status_data.get("message", "未知状态")
                        if status_code == 0:  # 登录成功
                            self.status_text.value = "🎉 登录成功！正在处理数据..."
                            save_log_to_file("登录成功，正在处理数据...", level="INFO")
                            self.page.update()
                            self.is_polling = False
                            # 提取 Cookie 数据
                            set_cookies = response.headers.get("set-cookie", "")
                            cookies_dict = self.parse_set_cookie(set_cookies)
                            cookie_string = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
                            # 访问 https://bilibili.com 以获取完整的 Cookie
                            save_log_to_file(f"通过访问 B 站主站获取完整的 Cookie", level="DEBUG")
                            resp = requests.get("https://www.bilibili.com", cookies=cookies_dict)
                            if resp.status_code == 200:
                                set_cookies = resp.headers.get("set-cookie", "")
                                cookies_dict = self.parse_set_cookie(set_cookies)
                                cookie_string = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
                            # 访问 https://link.bilibili.com/p/center/index#/my-room/start-live 以获取完整的 Cookie
                            save_log_to_file(f"通过访问直播管理获取完整的 Cookie", level="DEBUG")
                            resp = requests.get("https://link.bilibili.com/p/center/index#/my-room/start-live", cookies=cookies_dict)
                            if resp.status_code == 200:
                                set_cookies = resp.headers.get("set-cookie", "")
                                cookies_dict = self.parse_set_cookie(set_cookies)
                                cookie_string = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])
                            # 将 Cookie 数据存储到 page 对象中，供 main.py 使用
                            self.page.login_cookies = cookie_string
                            # 记录日志
                            with open("logs/gui.log", "a", encoding="utf-8") as f:
                                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] 登录成功，获取到的 Cookies: {cookie_string}\n")
                                f.write("-" * 50 + "\n")
                            # 返回主页面
                            self.page.route = "/main"
                            self.page.update()
                            return
                        elif status_code == 86101:  # 未扫码
                            self.status_text.value = "等待扫码中..."
                            save_log_to_file("等待扫码中...", level="DEBUG")
                        elif status_code == 86090:  # 已扫码未确认
                            self.status_text.value = "已扫码，请在手机上确认登录"
                            save_log_to_file("已扫码，请在手机上确认登录", level="DEBUG")
                        else:
                            self.status_text.value = f"状态：{status_msg}"
                            save_log_to_file(f"未知状态：{status_msg}", level="DEBUG")
                        self.page.update()
            except Exception as e:
                self.status_text.value = f"❌ 轮询错误：{str(e)}"
                save_log_to_file(f"轮询错误：{str(e)}", level="ERROR")
                self.page.update()
            time.sleep(1)  # 每 1 秒轮询一次

    def parse_set_cookie(self, set_cookie_header):
        """解析 Set-Cookie 头部，返回 cookie 字典"""
        cookies = {}
        if not set_cookie_header:
            return cookies
        cookie_pairs = set_cookie_header.split(",")
        for pair in cookie_pairs:
            pair = pair.strip()
            if ";" in pair:
                cookie_part = pair.split(";")[0].strip()
                if "=" in cookie_part:
                    key, value = cookie_part.split("=", 1)
                    cookies[key.strip()] = value.strip()
        return cookies

    def stop_polling(self):
        """停止轮询"""
        self.is_polling = False

def get_qr_login_content(page: ft.Page):
    # 创建新页面内容
    qr_image = ft.Image(
        src="",  # 初始为空
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN,
    )
    status_text = ft.Text(
        value="正在生成二维码...",
        size=18,
        text_align=ft.TextAlign.CENTER,
    )
    back_button = ft.ElevatedButton(
        text="返回",
        width=150,
        on_click=lambda e: handle_back_button(e, login_client)
    )

    # 创建列布局，确保垂直居中
    qr_login_content = ft.Column(
        controls=[
            qr_image,
            status_text,
            back_button
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # 创建容器，确保整体内容水平垂直居中
    qr_login_container = ft.Container(
        content=qr_login_content,
        alignment=ft.alignment.center,
        expand=True
    )

    # 创建登录客户端实例
    login_client = QRLoginClient(status_text, qr_image, page)
    # 启动二维码生成
    login_client.generate_qr_code()

    return qr_login_container

def handle_back_button(e, login_client):
    """处理返回按钮点击事件，停止轮询并返回主页面"""
    login_client.stop_polling()
    e.page.route = "/main"
    e.page.update()