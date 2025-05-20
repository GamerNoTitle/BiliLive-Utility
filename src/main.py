import flet as ft
import os
import sys
from home import get_main_content
from login import get_qr_login_content

# 强制设置 UTF-8 编码
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
else:
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)

# 确保文件系统编码支持中文路径
if 'PYTHONUTF8' not in os.environ:
    os.environ['PYTHONUTF8'] = '1'

def app_main(page: ft.Page):
    # 设置页面基本属性
    page.title = "B 站直播管理小助手 - GamerNoTitle"
    page.fonts = {
        "Source Hans Sans": "/SourceHanSansCN-Normal.otf"
    }
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_height = 1280
    page.window_width = 900
    page.window_resizable = False
    page.padding = 20
    page.adaptive = True
    page.scroll = ft.ScrollMode.AUTO

    # 设置主题
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.DEEP_PURPLE_200,
            secondary=ft.Colors.DEEP_PURPLE_100,
            surface=ft.Colors.DEEP_PURPLE_50,
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.BLACK,
            on_surface=ft.Colors.BLACK,
        ),
        visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
    )

    # 用于存储登录成功后的 Cookie 数据
    page.login_cookies = ""
    page.login_roomid = ""  # 存储从 API 获取的直播间 ID

    # 定义路由视图
    def route_change(route):
        page.views.clear()
        if page.route == "/main":
            page.views.append(
                ft.View(
                    route="/main",
                    controls=[get_main_content(page)],
                    scroll=ft.ScrollMode.AUTO
                )
            )
        elif page.route == "/qr-login":
            page.views.append(
                ft.View(
                    route="/qr-login",
                    controls=[get_qr_login_content(page)],
                )
            )
        page.update()

    # 设置初始路由和视图
    page.on_route_change = route_change
    page.route = "/main"  # 初始页面为主页面
    route_change(page.route)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    with open("logs/latest.log", "w") as f:
        f.close()
    ft.app(target=app_main)