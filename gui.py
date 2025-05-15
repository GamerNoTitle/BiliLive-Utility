import flet as ft
import requests
import os
import json
from datetime import datetime

def parse_cookie_string(cookie_string):
    """将 Cookie 字符串解析为字典形式"""
    cookie_dict = {}
    if not cookie_string:
        return cookie_dict
    pairs = cookie_string.split(";")
    for pair in pairs:
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)
            cookie_dict[key.strip()] = value.strip()
    return cookie_dict

def save_stream_info(roomid, addr, code):
    """将推流信息保存到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"stream_info_{roomid}_{timestamp.replace(':', '').replace('-', '').replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"直播间号: {roomid}\n")
        f.write(f"推流地址: {addr}\n")
        f.write(f"推流密钥: {code}\n")
        f.write(f"生成时间: {timestamp}\n")
    return filename

def save_log_to_file(log_content):
    """将日志保存到 logs/gui.log 文件中，如果文件夹不存在则创建"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "gui.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {log_content}\n")
        f.write("-" * 50 + "\n")

def main(page: ft.Page):
    page.title = "B站快速开播及推流码获取工具 - GamerNoTitle"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.window_resizable = False
    page.padding = 20
    page.adaptive = True

    # 设置主题色为主色调 DEEP_PURPLE_200
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.DEEP_PURPLE_200,
            secondary=ft.Colors.DEEP_PURPLE_100,
            surface=ft.Colors.DEEP_PURPLE_50,
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.BLACK,
            on_surface=ft.Colors.BLACK
        ),
        visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY
    )

    welcome_text = ft.Text(
        value="Bilibili 直播开播及凭据获取工具\nMade by GamerNoTitle\nhttps://github.com/GamerNoTitle/Bililive-Identity-Grabber",
        text_align=ft.TextAlign.CENTER,
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.INDIGO_500
    )

    # 直播间号和 Cookies 输入框
    roomid_input = ft.TextField(
        label="直播间号",
        hint_text="请输入你的直播间号",
        width=550
    )
    cookies_input = ft.TextField(
        label="Cookies",
        hint_text="请输入你的 Cookies（从浏览器开发者工具中获取）",
        width=550,
        multiline=False
    )
    input_row = ft.Row(
        controls=[roomid_input, cookies_input],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # 推流地址
    def copy_addr_to_clipboard(e):
        if stream_addr_input.value:
            page.set_clipboard(stream_addr_input.value)
            result_text.value = "🎉 推流地址已复制到剪贴板！"
        else:
            result_text.value = "❌ 推流地址为空，无法复制！"
        page.update()

    stream_addr_input = ft.TextField(
        label="推流地址",
        width=1000,
        read_only=True,
        hint_text="请先开播，开播成功后会展示地址的 🤔"
    )
    copy_addr_button = ft.ElevatedButton(text="复制", width=100, on_click=copy_addr_to_clipboard)
    addr_row = ft.Row(
        controls=[stream_addr_input, copy_addr_button],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # 推流密钥
    def copy_code_to_clipboard(e):
        if stream_code_input.value:
            page.set_clipboard(stream_code_input.value)
            result_text.value = "🎉 推流密钥已复制到剪贴板！"
        else:
            result_text.value = "❌ 推流密钥为空，无法复制！"
        page.update()

    stream_code_input = ft.TextField(
        label="推流密钥",
        width=1000,
        read_only=True,
        hint_text="请先开播，开播成功后会展示密钥的 🤔"
    )
    copy_code_button = ft.ElevatedButton(text="复制", width=100, on_click=copy_code_to_clipboard)
    code_row = ft.Row(
        controls=[stream_code_input, copy_code_button],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # 保存凭据到本地的 Checkbox
    save_checkbox = ft.Checkbox(
        label="保存推流凭据到本地",
        value=False
    )
    checkbox_row = ft.Row(
        controls=[save_checkbox],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 操作结果显示区域
    result_text = ft.Text(value="", size=18, text_align=ft.TextAlign.CENTER, width=1000)

    # 日志内容（用于保存到文件）
    log_content = ""

    # 按钮
    start_button = ft.ElevatedButton(text="开播", width=150, on_click=lambda e: start_live_clicked(e))
    stop_button = ft.ElevatedButton(text="停播", width=150, on_click=lambda e: stop_live_clicked(e), disabled=True)
    github_button = ft.ElevatedButton(text="GitHub", width=150, on_click=lambda e: page.launch_url("https://github.com/GamerNoTitle/Bililive-Identity-Grabber"))
    button_row = ft.Row(
        controls=[start_button, stop_button, github_button],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 定义按钮点击事件
    def start_live_clicked(e):
        nonlocal log_content
        log_content = ""
        result_text.value = ""
        stream_addr_input.value = ""
        stream_code_input.value = ""
        roomid = roomid_input.value.strip()
        cookie_string = cookies_input.value.strip()

        if not roomid:
            result_text.value = "❌ 错误：直播间号不能为空！"
            page.update()
            return
        if not cookie_string:
            result_text.value = "❌ 错误：Cookies 不能为空！"
            page.update()
            return

        cookies = parse_cookie_string(cookie_string)
        if not cookies:
            result_text.value = "❌ 错误：解析 Cookies 失败，请检查是否正确复制！"
            page.update()
            return

        csrf = cookies.get("bili_jct")
        if not csrf:
            result_text.value = "❌ 错误：未找到 bili_jct，请检查 Cookies 是否完整！"
            page.update()
            return

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://link.bilibili.com",
            "referer": "https://link.bilibili.com/p/center/index",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        }

        start_data_bls = {
            "room_id": roomid,
            "platform": "pc_link",
            "area_v2": "624",
            "backup_stream": "0",
            "csrf_token": csrf,
            "csrf": csrf,
        }

        try:
            log_content += "正在发送开播请求...\n"
            result_text.value = "正在发送开播请求..."
            page.update()
            start_resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/startLive",
                cookies=cookies,
                headers=headers,
                data=start_data_bls,
            ).json()

            log_content += f"开播响应: {json.dumps(start_resp, indent=2, ensure_ascii=False)}\n"
            if start_resp.get("code") == 0:
                rtmp_data = start_resp.get("data", {}).get("rtmp", {})
                addr = rtmp_data.get("addr", "❌ 找不到推流地址！")
                code = rtmp_data.get("code", "❌ 找不到推流密钥！")
                stream_addr_input.value = addr
                stream_code_input.value = code
                
                if save_checkbox.value:  # 只有勾选时才保存到文件
                    filename = save_stream_info(roomid, addr, code)
                    result_text.value = f"🎉 开播成功！推流信息已显示。记得去网页端更改你的直播分类哦！\n直播凭据已保存到当前目录的 {filename} 文件中。"
                    log_content += f"\n🎉 开播成功！推流信息如下：\n"
                    log_content += f"推流地址：{addr}\n"
                    log_content += f"推流密钥（推流码）：{code}\n"
                    log_content += f"推流信息已保存到文件: {filename}\n"
                else:
                    result_text.value = "🎉 开播成功！推流信息已显示。记得去网页端更改你的直播分类哦！"
                    log_content += f"\n🎉 开播成功！推流信息如下：\n"
                    log_content += f"推流地址：{addr}\n"
                    log_content += f"推流密钥（推流码）：{code}\n"
                    log_content += "未保存推流信息到本地。\n"
                # 开播成功后禁用开播按钮，启用停播按钮
                start_button.disabled = True
                stop_button.disabled = False
            else:
                result_text.value = f"❌ 开播失败！错误信息：{start_resp.get('message', '未知错误')}"
                log_content += f"\n❌ 开播失败！错误信息：{start_resp.get('message', '未知错误')}\n"
        except requests.exceptions.RequestException as err:
            result_text.value = "❌ 网络请求错误！请检查网络或 Cookies。"
            log_content += f"\n❌ 网络请求错误：{err}\n请检查网络连接或 Cookies 是否有效（可能已过期）。\n"
        except Exception as err:
            result_text.value = "❌ 未知错误！请检查输入信息。"
            log_content += f"\n❌ 发生未知错误：{err}\n请检查输入信息或稍后重试。\n"
        # 保存日志到文件
        save_log_to_file(log_content)
        page.update()

    def stop_live_clicked(e):
        nonlocal log_content
        log_content = ""
        result_text.value = ""
        roomid = roomid_input.value.strip()
        cookie_string = cookies_input.value.strip()

        if not roomid:
            result_text.value = "错误：直播间号不能为空！"
            page.update()
            return
        if not cookie_string:
            result_text.value = "错误：Cookies 不能为空！"
            page.update()
            return

        cookies = parse_cookie_string(cookie_string)
        if not cookies:
            result_text.value = "错误：解析 Cookies 失败，请检查是否正确复制！"
            page.update()
            return

        csrf = cookies.get("bili_jct")
        if not csrf:
            result_text.value = "错误：未找到 bili_jct，请检查 Cookies 是否完整！"
            page.update()
            return

        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://link.bilibili.com",
            "referer": "https://link.bilibili.com/p/center/index",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        }

        stop_data_bls = {
            "room_id": roomid,
            "platform": "pc_link",
            "csrf_token": csrf,
            "csrf": csrf,
        }

        try:
            log_content += "正在发送停播请求...\n"
            result_text.value = "正在发送停播请求..."
            page.update()
            stop_resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/stopLive",
                cookies=cookies,
                headers=headers,
                data=stop_data_bls,
            ).json()

            log_content += f"停播响应: {json.dumps(stop_resp, indent=2, ensure_ascii=False)}\n"
            if stop_resp.get("code") == 0:
                result_text.value = "🎉 停播成功！"
                log_content += "\n🎉 停播成功！\n"
                # 停播成功后启用开播按钮，禁用停播按钮
                start_button.disabled = False
                stop_button.disabled = True
            else:
                result_text.value = f"❌ 停播失败！错误信息：{stop_resp.get('message', '未知错误')}"
                log_content += f"\n❌ 停播失败！错误信息：{stop_resp.get('message', '未知错误')}\n"
        except requests.exceptions.RequestException as err:
            result_text.value = "❌ 网络请求错误！请检查网络或 Cookies。"
            log_content += f"\n❌ 网络请求错误：{err}\n请检查网络连接或 Cookies 是否有效（可能已过期）。\n"
        except Exception as err:
            result_text.value = "❌ 未知错误！请检查输入信息。"
            log_content += f"\n❌ 发生未知错误：{err}\n请检查输入信息或稍后重试。\n"
        # 保存日志到文件
        save_log_to_file(log_content)
        page.update()

    # 布局
    page.add(
        welcome_text,
        ft.Divider(height=20),
        input_row,
        ft.Divider(height=20),
        addr_row,
        code_row,
        checkbox_row,
        ft.Divider(height=20),
        button_row,
        ft.Divider(height=20),
        result_text,
    )

if __name__ == "__main__":
    ft.app(target=main)