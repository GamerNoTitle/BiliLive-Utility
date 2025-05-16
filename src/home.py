import flet as ft
import requests
import os
import json
from datetime import datetime
import time

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://link.bilibili.com",
    "referer": "https://link.bilibili.com/p/center/index",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
}

areas = {}
prev_tags = []
prev_title = ""

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

def save_log_to_file(log_content, level="INFO"):
    """将日志保存到 logs/gui.log 文件中，如果文件夹不存在则创建，并根据级别保存到不同文件"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 保存到 gui.log (所有日志)
    log_file = os.path.join(log_dir, "gui.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{level}] {log_content}\n")
        f.write("-" * 50 + "\n")

def save_config_to_file(roomid, cookie_string):
    """将配置保存到 config.json 文件中"""
    config = {"roomid": roomid, "cookies": cookie_string}
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    save_log_to_file(f"配置已保存到 config.json 文件中", level="INFO")

def get_user_room_id(mid, cookies_string):
    """通过用户 ID 获取直播间 ID"""
    try:
        resp = requests.get(
            "https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld",
            params={"mid": mid},
            headers=HEADERS,
            cookies=parse_cookie_string(cookies_string)
        )
        if resp.status_code == 200:
            data = resp.json()
            save_log_to_file(f"获取直播间信息响应: {json.dumps(data, ensure_ascii=False)}", level="DEBUG")
            if data.get("code") == 0:
                room_id = data.get("data", {}).get("roomid", 0)
                if room_id:
                    save_log_to_file(f"成功获取直播间 ID: {room_id}", level="INFO")
                    with open("config.json", "w") as f:
                        f.write(json.dumps({"roomid": room_id, "cookies": cookies_string}, ensure_ascii=False, indent=4))
                    return str(room_id)
                else:
                    save_log_to_file("未找到直播间 ID", level="ERROR")
                    return ""
            else:
                save_log_to_file(f"获取直播间信息失败: {data.get('message', '未知错误')}", level="ERROR")
                return ""
        else:
            save_log_to_file(f"获取直播间信息失败，状态码: {resp.status_code}, 响应: {resp.text}", level="ERROR")
            return ""
    except Exception as e:
        save_log_to_file(f"获取直播间 ID 时发生错误: {str(e)}", level="ERROR")
        return ""

def get_main_content(page: ft.Page):
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    welcome_text = ft.Text(
        value="B 站直播管理小助手\nhttps://github.com/GamerNoTitle/BiliLive-Utility",
        text_align=ft.TextAlign.CENTER,
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.INDIGO_500,
    )

    manage_liveroom_text = ft.Text(
        value="管理你的直播间",
        text_align=ft.TextAlign.CENTER,
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.INDIGO_500,
    )

    get_liveroom_data_btn = ft.ElevatedButton(
        text="获取直播间数据",
        width=150,
        on_click=lambda e: get_liveroom_data_clicked(e),
    )

    # 直播间管理标题行
    liveroom_title = ft.TextField(
        label="直播间标题",
        hint_text="直接输入或者点击获取直播间信息按钮获取",
        width=1000,
    )

    def update_liveroom_title_clicked(e):
        """更新直播间标题"""
        global prev_title
        title = liveroom_title.value.strip()
        cookies_string = cookies_input.value.strip()
        if roomid_input.value.strip() == "":
            result_text.value = "❌ 错误：直播间号不能为空！"
            save_log_to_file("直播间号为空", level="ERROR")
            page.update()
            return
        if prev_title == "":
            result_text.value = "❌ 错误：你必须先获取直播间信息才能对其进行修改！"
            save_log_to_file(
                "用户在尝试修改标题的时候未先获取直播间信息", level="ERROR"
            )
            page.update()
            return
        if cookies_string == "":
            result_text.value = "❌ 错误：Cookies 不能为空！"
            save_log_to_file("Cookies 为空", level="ERROR")
            page.update()
            return
        if not title:
            result_text.value = "❌ 错误：直播间标题不能为空！"
            save_log_to_file("直播间标题为空", level="ERROR")
            page.update()
            return
        if len(title) > 41:
            result_text.value = "❌ 错误：直播间标题长度不能超过 41 个字符！"
            save_log_to_file(f"直播间标题 {title} 长度超过 41 个字符", level="ERROR")
            page.update()
            return
        data = {"room_id": roomid_input.value.strip(), "title": title, "csrf": parse_cookie_string(cookie_string=cookies_string).get("bili_jct")}
        resp = requests.post(
            "https://api.live.bilibili.com/room/v1/Room/update",
            cookies=parse_cookie_string(cookie_string=cookies_string),
            headers=HEADERS,
            data=data,
        )
        if resp.status_code == 200:
            if resp.json().get("code") == 0:
                result_text.value = f"🎉 更新直播间标题成功！当前状态：{resp.json().get('data', {}).get('audit_info', {}).get('audit_title_reason') if resp.json().get('data', {}).get('audit_info', {}).get('audit_title_reason') else '更改成功，没有触发审核！'}"
                save_log_to_file(
                    f"更新直播间标题成功！当前状态：{resp.json().get('data', {}).get('audit_info', {}).get('audit_title_reason') if resp.json().get('data', {}).get('audit_info', {}).get('audit_title_reason') else '更改成功，没有触发审核！'}",
                    level="INFO",
                )
                prev_title = title
            else:
                result_text.value = f"❌ 更新直播间标题失败！错误信息：{resp.json().get('message', '未知错误')}"
                save_log_to_file(
                    f"更新直播间标题失败！错误信息：{resp.json().get('message', '未知错误')}",
                    level="ERROR",
                )
        else:
            try:
                data = resp.json()
                save_log_to_file(json.dumps(data), level="DEBUG")
                result_text.value = f"更新直播间标题失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                save_log_to_file(
                    f"更新直播间标题失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                    level="ERROR",
                )
            except json.JSONDecodeError:
                result_text.value = f"更新直播间标题失败！错误信息：{resp.text}"
                save_log_to_file(
                    f"更新直播间标题失败！错误信息：{resp.text}", level="ERROR"
                )
        page.update()

    liveroom_title_update_btn = ft.ElevatedButton(
        text="更新",
        width=100,
        on_click=lambda e: update_liveroom_title_clicked(e),
    )

    liveroom_tags_field = ft.TextField(
        label="直播间标签（以逗号分割，不分半角全角，尽量不要太长、太多，程序未对过长过多的 tag 进行校验）",
        hint_text="直接输入或者点击获取直播间信息按钮获取",
        width=1000,
    )

    def update_liveroom_tags_clicked(e):
        """更新直播间标签"""
        global prev_tags
        result_text.value = "⚠️ 因为 B 站对操作有频率限制，所以修改 tag 需要的时间较久，请耐心等待！"
        page.update()
        tags = set(liveroom_tags_field.value.strip().replace("，", ",").split(","))
        cookies_string = cookies_input.value.strip()
        if roomid_input.value.strip() == "":
            result_text.value = "❌ 错误：直播间号不能为空！"
            save_log_to_file("直播间号为空", level="ERROR")
            page.update()
            return
        if cookies_string == "":
            result_text.value = "❌ 错误：Cookies 不能为空！"
            save_log_to_file("Cookies 为空", level="ERROR")
            page.update()
            return
        if prev_tags == []:
            result_text.value = "❌ 错误：你必须先获取直播间信息才能对其进行修改！"
            save_log_to_file(
                "用户在尝试修改标签的时候未先获取直播间信息", level="ERROR"
            )
            page.update()
            return
        if not tags:
            result_text.value = "❌ 错误：直播间标签不能为空！"
            save_log_to_file("直播间标签为空", level="ERROR")
            page.update()
            return
        for tag in tags:
            if len(tag) > 20:
                result_text.value = f"❌ 错误：直播间单个标签长度不能超过 128 个字符！标签 {tag} 超过 128 个字符"
                save_log_to_file(
                    f"直播间单个标签 {tag} 长度超过 128 个字符", level="ERROR"
                )
                page.update()
                return
        # 先删除原有的 tag
        for tag in prev_tags:
            data = {"room_id": roomid_input.value.strip(), "del_tag": tag, "csrf": parse_cookie_string(cookie_string=cookies_string).get("bili_jct")}
            resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/update",
                cookies=parse_cookie_string(cookie_string=cookies_string),
                headers=HEADERS,
                data=data,
            )
            if resp.status_code == 200:
                if resp.json().get("code") == 0:
                    save_log_to_file(
                        f"删除直播间标签成功！当前状态：{resp.json().get('data', {}).get('audit_info', {}).get('audit_tag_reason') if resp.json().get('data', {}).get('audit_info', {}).get('audit_tag_reason') else '更改成功，没有触发审核！'}",
                        level="INFO",
                    )
                else:
                    result_text.value = f"❌ 处理 tag 时出现了问题！错误信息：{resp.json().get('message', '未知错误')}"
                    save_log_to_file(
                        f"删除直播间标签失败！错误信息：{resp.json().get('message', '未知错误')}",
                        level="ERROR",
                    )
                    page.update()
                    return
            else:
                try:
                    data = resp.json()
                    save_log_to_file(json.dumps(data), level="DEBUG")
                    result_text.value = f"❌ 处理 tag 时出现了问题！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                    save_log_to_file(
                        f"删除直播间标签失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                        level="ERROR",
                    )
                    page.update()
                    return
                except json.JSONDecodeError:
                    result_text.value = (
                        f"❌ 处理 tag 时出现了问题！错误信息：{resp.text}"
                    )
                    save_log_to_file(
                        f"删除直播间标签失败！错误信息：{resp.text}", level="ERROR"
                    )
            time.sleep(3)
        for tag in tags:
            data = {"room_id": roomid_input.value.strip(), "add_tag": tag, "csrf": parse_cookie_string(cookie_string=cookies_string).get("bili_jct")}
            resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/update",
                cookies=parse_cookie_string(cookie_string=cookies_string),
                headers=HEADERS,
                data=data,
            )
            if resp.status_code == 200:
                if resp.json().get("code") == 0:
                    save_log_to_file(
                        f"添加直播间标签成功！当前状态：{resp.json().get('data', {}).get('audit_info', {}).get('audit_tag_reason') if resp.json().get('data', {}).get('audit_info', {}).get('audit_tag_reason') else '更改成功，没有触发审核！'}",
                        level="INFO",
                    )
                else:
                    result_text.value = f"❌ 处理 tag 时出现了问题！错误信息：{resp.json().get('message', '未知错误')}"
                    save_log_to_file(
                        f"添加直播间标签失败！错误信息：{resp.json().get('message', '未知错误')}",
                        level="ERROR",
                    )
                    page.update()
                    return
            else:
                try:
                    data = resp.json()
                    save_log_to_file(json.dumps(data), level="DEBUG")
                    result_text.value = f"❌ 处理 tag 时出现了问题！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                    save_log_to_file(
                        f"添加直播间标签失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                        level="ERROR",
                    )
                    page.update()
                    return
                except json.JSONDecodeError:
                    result_text.value = (
                        f"❌ 处理 tag 时出现了问题！错误信息：{resp.text}"
                    )
                    save_log_to_file(
                        f"添加直播间标签失败！错误信息：{resp.text}", level="ERROR"
                    )
            time.sleep(3)
        result_text.value = "🎉 更新直播间标签成功！"
        save_log_to_file("更新直播间标签成功", level="INFO")
        page.update()
        # 更新成功后，更新 prev_tags
        prev_tags = tags

    liveroom_tags_update_btn = ft.ElevatedButton(
        text="更新",
        width=100,
        on_click=lambda e: update_liveroom_tags_clicked(e),
    )

    def set_area_by_parent_area(e):
        """根据父分区设置子分区"""
        if liveroom_parent_area.value:
            save_log_to_file(
                f"选择的父分区: {liveroom_parent_area.value}", level="DEBUG"
            )
            liveroom_area.value = ft.dropdown.Option()
            parent_area_id = int(liveroom_parent_area.value.split("(")[-1].strip(")"))
            for area in areas:
                if area["id"] == parent_area_id:
                    subarea_list = area.get("list", [])
                    liveroom_area.options = [
                        ft.dropdown.Option(f"{subarea['name']}({subarea['id']})")
                        for subarea in subarea_list
                    ]
            liveroom_area.options.append(ft.dropdown.Option("-- 请选择子分区 --"))
            liveroom_area.value = "-- 请选择子分区 --"
        else:
            liveroom_area.options = []
        page.update()

    liveroom_parent_area = ft.Dropdown(
        label="直播间父分区",
        hint_text="选择直播间父分区",
        width=450,
        options=[],
        on_change=set_area_by_parent_area,
    )

    liveroom_area = ft.Dropdown(
        label="直播间分区",
        hint_text="选择直播间分区",
        width=450,
        options=[],
        on_change=lambda e: save_log_to_file(
            f"选择的分区: {liveroom_area.value}", level="DEBUG"
        ),
    )

    def update_liveroom_area_clicked(e):
        room_id = roomid_input.value.strip()
        if liveroom_area.value == "-- 请选择子分区 --":
            result_text.value = "❌ 错误：请选择直播间分区！"
            save_log_to_file("直播间分区未选择", level="ERROR")
            page.update()
            return
        area_id = int(liveroom_area.value.split("(")[-1].strip(")"))
        resp = requests.post(
            "https://api.live.bilibili.com/room/v1/Room/update",
            cookies=parse_cookie_string(cookie_string=cookies_input.value.strip()),
            headers=HEADERS,
            data={
                "room_id": room_id,
                "area_id": area_id,
                "csrf": parse_cookie_string(cookie_string=cookies_input.value.strip()).get("bili_jct"),
            },
        )
        if resp.status_code == 200:
            if resp.json().get("code") == 0:
                result_text.value = "🎉 更新直播间分区成功！"
                save_log_to_file("更新直播间分区成功", level="INFO")
            else:
                result_text.value = f"❌ 更新直播间分区失败！错误信息：{resp.json().get('message', '未知错误')}"
                save_log_to_file(
                    f"更新直播间分区失败！错误信息：{resp.json().get('message', '未知错误')}",
                    level="ERROR",
                )
        else:
            try:
                data = resp.json()
                save_log_to_file(json.dumps(data), level="DEBUG")
                result_text.value = f"更新直播间分区失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                save_log_to_file(
                    f"更新直播间分区失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                    level="ERROR",
                )
            except json.JSONDecodeError:
                result_text.value = f"更新直播间分区失败！错误信息：{resp.text}"
                save_log_to_file(
                    f"更新直播间分区失败！错误信息：{resp.text}", level="ERROR"
                )
        page.update()

    liveroom_area_update_btn = ft.ElevatedButton(
        text="更新分区",
        width=190,
        on_click=lambda e: update_liveroom_area_clicked(e),
    )

    manage_liveroom_hint_row = ft.Row(
        controls=[manage_liveroom_text, get_liveroom_data_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    manage_liveroom_title_row = ft.Row(
        controls=[liveroom_title, liveroom_title_update_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    manage_liveroom_tags_row = ft.Row(
        controls=[liveroom_tags_field, liveroom_tags_update_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    manage_liveroom_area_row = ft.Row(
        controls=[liveroom_parent_area, liveroom_area, liveroom_area_update_btn],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 直播间号和 Cookies 输入框
    roomid_input = ft.TextField(
        label="直播间号",
        hint_text="请输入你的直播间号",
        width=550,
        value=config.get("roomid", ""),
    )
    cookies_input = ft.TextField(
        label="Cookies",
        hint_text="请输入你的 Cookies（从浏览器开发者工具中获取）",
        width=550,
        multiline=False,
        value=config.get("cookies", ""),
        password=True,
        on_focus=lambda e: handle_cookie_focus(e),
        on_blur=lambda e: handle_cookie_blur(e),
    )

    def handle_cookie_focus(e):
        """聚焦时显示明文"""
        cookies_input.password = False
        page.update()

    def handle_cookie_blur(e):
        """失去焦点时隐藏内容"""
        if cookies_input.value:  # 如果有内容，则设置为密码模式
            cookies_input.password = True
        else:  # 如果没有内容，则不设置为密码模式，以便显示 hint_text
            cookies_input.password = False
        page.update()

    input_row = ft.Row(
        controls=[roomid_input, cookies_input],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 新增扫码登录按钮
    def show_qr_login_page(e):
        page.route = "/qr-login"
        page.update()

    qr_login_button = ft.ElevatedButton(
        text="扫码登录",
        width=150,
        on_click=show_qr_login_page
    )
    qr_login_row = ft.Row(
        controls=[qr_login_button],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
        hint_text="请先开播，开播成功后会展示地址的 🤔",
    )
    copy_addr_button = ft.ElevatedButton(
        text="复制", width=100, on_click=copy_addr_to_clipboard
    )
    addr_row = ft.Row(
        controls=[stream_addr_input, copy_addr_button],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
        hint_text="请先开播，开播成功后会展示密钥的 🤔",
    )
    copy_code_button = ft.ElevatedButton(
        text="复制", width=100, on_click=copy_code_to_clipboard
    )
    code_row = ft.Row(
        controls=[stream_code_input, copy_code_button],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 保存凭据到本地的 Checkbox
    save_checkbox = ft.Checkbox(label="保存推流凭据到本地", value=False)
    checkbox_row = ft.Row(
        controls=[save_checkbox], alignment=ft.MainAxisAlignment.CENTER
    )

    # 操作结果显示区域
    result_text = ft.Text(value="欢迎使用 BiliLive Utility 工具箱！本程序的所有提示会在这里显示 =w=\n如果本工具显示不全的话，可以把本工具的窗口拉大来，或者滚动浏览使用。", size=18, text_align=ft.TextAlign.CENTER, width=1000)

    # 按钮
    start_button = ft.ElevatedButton(
        text="开播", width=150, on_click=lambda e: start_live_clicked(e)
    )
    stop_button = ft.ElevatedButton(
        text="停播", width=150, on_click=lambda e: stop_live_clicked(e), disabled=True
    )
    github_button = ft.ElevatedButton(
        text="GitHub",
        width=150,
        on_click=lambda e: page.launch_url(
            "https://github.com/GamerNoTitle/Bililive-Credential-Grabber"
        ),
    )
    button_row = ft.Row(
        controls=[start_button, stop_button, github_button],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # 开播按钮点击
    def start_live_clicked(e):
        result_text.value = ""
        stream_addr_input.value = ""
        stream_code_input.value = ""
        roomid = roomid_input.value.strip()
        cookie_string = cookies_input.value.strip()

        if not roomid:
            result_text.value = "❌ 错误：直播间号不能为空！"
            save_log_to_file("直播间号不能为空", level="ERROR")
            page.update()
            return
        if not cookie_string:
            result_text.value = "❌ 错误：Cookies 不能为空！"
            save_log_to_file("Cookies 不能为空", level="ERROR")
            page.update()
            return

        cookies = parse_cookie_string(cookie_string)
        if not cookies:
            result_text.value = "❌ 错误：解析 Cookies 失败，请检查是否正确复制！"
            save_log_to_file("解析 Cookies 失败", level="ERROR")
            page.update()
            return

        csrf = cookies.get("bili_jct")
        if not csrf:
            result_text.value = "❌ 错误：未找到 bili_jct，请检查 Cookies 是否完整！"
            save_log_to_file("未找到 bili_jct", level="ERROR")
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
            "area_v2": liveroom_area.value.split("(")[-1].strip(")"),
            "backup_stream": "0",
            "csrf_token": csrf,
            "csrf": csrf,
        }

        try:
            result_text.value = "正在发送开播请求..."
            save_log_to_file("正在发送开播请求", level="INFO")
            page.update()
            start_resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/startLive",
                cookies=cookies,
                headers=HEADERS,
                data=start_data_bls,
            ).json()

            # 将详细响应作为 DEBUG 级别日志
            save_log_to_file(
                f"开播响应: {json.dumps(start_resp, indent=2, ensure_ascii=False)}",
                level="DEBUG",
            )

            if start_resp.get("code") == 0:
                rtmp_data = start_resp.get("data", {}).get("rtmp", {})
                addr = rtmp_data.get("addr", "❌ 找不到推流地址！")
                code = rtmp_data.get("code", "❌ 找不到推流密钥！")
                stream_addr_input.value = addr
                stream_code_input.value = code
                if save_checkbox.value:  # 只有勾选时才保存到文件
                    filename = save_stream_info(roomid, addr, code)
                    result_text.value = f"🎉 开播成功！推流信息已显示。\n直播凭据已保存到当前目录的 {filename} 文件中。"
                    save_log_to_file(
                        f"开播成功！直播凭据已保存到当前目录的 {filename} 文件中。",
                        level="INFO",
                    )
                    save_log_to_file(
                        f"推流地址：{addr}\n推流密钥：{code[0] + (len(code)-2) * '*' + code[-1]}",
                        level="DEBUG",
                    )

                else:
                    result_text.value = (
                        "🎉 开播成功！推流信息已显示。"
                    )
                    save_log_to_file("开播成功！推流信息已显示。", level="INFO")
                    save_log_to_file(
                        f"推流地址：{addr}\n推流密钥：{code[0] + (len(code)-2) * '*' + code[-1]}",
                        level="DEBUG",
                    )
                # 开播成功后禁用开播按钮，启用停播按钮
                save_config_to_file(roomid, cookie_string)
                start_button.disabled = True
                stop_button.disabled = False
            else:
                result_text.value = (
                    f"❌ 开播失败！错误信息：{start_resp.get('message', '未知错误')}"
                )
                save_log_to_file(
                    f"开播失败！错误信息：{start_resp.get('message', '未知错误')}",
                    level="ERROR",
                )
        except requests.exceptions.RequestException as err:
            result_text.value = "❌ 网络请求错误！请检查网络或 Cookies。"
            save_log_to_file(f"网络请求错误：{err}", level="ERROR")
        except Exception as err:
            result_text.value = "❌ 未知错误！请检查输入信息。"
            save_log_to_file(f"发生未知错误：{err}", level="ERROR")
        page.update()

    # 停播按钮点击
    def stop_live_clicked(e):
        result_text.value = ""
        roomid = roomid_input.value.strip()
        cookie_string = cookies_input.value.strip()

        if not roomid:
            result_text.value = "错误：直播间号不能为空！"
            save_log_to_file("直播间号不能为空", level="ERROR")
            page.update()
            return
        if not cookie_string:
            result_text.value = "错误：Cookies 不能为空！"
            save_log_to_file("Cookies 不能为空", level="ERROR")
            page.update()
            return

        cookies = parse_cookie_string(cookie_string)
        if not cookies:
            result_text.value = "错误：解析 Cookies 失败，请检查是否正确复制！"
            save_log_to_file("解析 Cookies 失败", level="ERROR")
            page.update()
            return

        csrf = cookies.get("bili_jct")
        if not csrf:
            result_text.value = "错误：未找到 bili_jct，请检查 Cookies 是否完整！"
            save_log_to_file("未找到 bili_jct", level="ERROR")
            page.update()
            return

        stop_data_bls = {
            "room_id": roomid,
            "platform": "pc_link",
            "csrf_token": csrf,
            "csrf": csrf,
        }

        try:
            result_text.value = "正在发送停播请求..."
            save_log_to_file("正在发送停播请求", level="INFO")
            page.update()
            stop_resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/stopLive",
                cookies=cookies,
                headers=HEADERS,
                data=stop_data_bls,
            ).json()

            # 将详细响应作为 DEBUG 级别日志
            save_log_to_file(
                f"停播响应: {json.dumps(stop_resp, indent=2, ensure_ascii=False)}",
                level="DEBUG",
            )

            if stop_resp.get("code") == 0:
                result_text.value = "🎉 停播成功！"
                save_log_to_file("停播成功", level="INFO")
                # 停播成功后启用开播按钮，禁用停播按钮
                start_button.disabled = False
                stop_button.disabled = True
            else:
                result_text.value = (
                    f"❌ 停播失败！错误信息：{stop_resp.get('message', '未知错误')}"
                )
                save_log_to_file(
                    f"停播失败！错误信息：{stop_resp.get('message', '未知错误')}",
                    level="ERROR",
                )
        except requests.exceptions.RequestException as err:
            result_text.value = "❌ 网络请求错误！请检查网络或 Cookies。"
            save_log_to_file(f"网络请求错误：{err}", level="ERROR")
        except Exception as err:
            result_text.value = "❌ 未知错误！请检查输入信息。"
            save_log_to_file(f"发生未知错误：{err}", level="ERROR")
        page.update()

    # 获取直播间信息按钮点击
    def get_liveroom_data_clicked(e):
        resp = requests.get(
            "https://api.live.bilibili.com/room/v1/Room/get_info",
            params={"room_id": roomid_input.value.strip()},
            headers=HEADERS,
        )
        save_log_to_file(resp.text, level="DEBUG")
        if resp.status_code == 200:
            data = resp.json()
            save_log_to_file(json.dumps(data), level="DEBUG")
            if data.get("code") == 0:
                room_data = data.get("data", {})
                room_title = room_data.get("title", "无法获取直播间标题")
                room_status = room_data.get("live_status", 0)
                room_tags = room_data.get("tags", []).split(",")
                room_area = (
                    (
                        room_data.get("parent_area_id", -1),
                        room_data.get("parent_area_name", "未知父分区"),
                    ),
                    (
                        room_data.get("area_id", -1),
                        room_data.get("area_name", "未知子分区"),
                    ),
                )
                global prev_title, prev_tags
                liveroom_title.value = room_title
                prev_title = room_title
                liveroom_tags_field.value = ", ".join(room_tags)
                prev_tags = room_tags
                liveroom_parent_area.value = f"{room_area[0][1]}({room_area[0][0]})"
                # 遍历已经获取的分区列表，找到对应的父分区，获取其子分区的列表后加入到子分区下拉框中
                for area in areas:
                    if area["id"] == room_area[0][0]:
                        subarea_list = area.get("list", [])
                        liveroom_area.options = [
                            ft.dropdown.Option(f"{subarea['name']}({subarea['id']})")
                            for subarea in subarea_list
                        ]
                        break
                liveroom_area.value = f"{room_area[1][1]}({room_area[1][0]})"
                result_text.value = (
                    f"成功获取直播间 {roomid_input.value.strip()} 的信息！"
                )
                save_log_to_file(
                    f"成功获取直播间 {roomid_input.value.strip()} 的信息！\n直播间标题: {room_title}\n直播间状态: {'在线' if room_status == 1 else ('轮播中' if room_status == 2 else '离线')}\n直播间标签: {', '.join(room_tags) if room_tags else '无标签'}\n直播间分区: {room_area[0][1]}({room_area[0][0]}) > {room_area[1][1]}({room_area[1][0]})",
                    level="INFO",
                )
            else:
                result_text.value = f"获取直播间信息失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                save_log_to_file(
                    f"获取直播间信息失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                    level="ERROR",
                )
        else:
            try:
                data = resp.json()
                save_log_to_file(json.dumps(data), level="DEBUG")
                result_text.value = f"获取直播间信息失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})"
                save_log_to_file(
                    f"获取直播间信息失败！错误信息：{data.get('msg', '未知错误')} ({data.get('code', 'unknown')})",
                    level="ERROR",
                )
            except json.JSONDecodeError:
                result_text.value = f"获取直播间信息失败！错误信息：{resp.text}"
                save_log_to_file(
                    f"获取直播间信息失败！错误信息：{resp.text}", level="ERROR"
                )
        page.update()

    # 检查是否有从登录页面返回的 Cookie 数据和直播间 ID
    def update_cookies_and_roomid_from_login():
        if hasattr(page, "login_cookies") and page.login_cookies:
            cookies_input.value = page.login_cookies
            result_text.value = "🎉 登录成功！Cookies 已更新！"
            save_log_to_file("通过扫码登录成功，Cookies 已更新", level="INFO")
            # 从 Cookie 中提取 DedeUserID
            cookies_dict = parse_cookie_string(page.login_cookies)
            dede_user_id = cookies_dict.get("DedeUserID", "")
            if dede_user_id:
                save_log_to_file(f"从 Cookie 提取 DedeUserID: {dede_user_id}", level="INFO")
                room_id = get_user_room_id(dede_user_id, page.login_cookies)
                if room_id:
                    roomid_input.value = room_id
                    result_text.value += f"\n🎉 已自动获取直播间 ID: {room_id}！"
                    save_log_to_file(f"已自动填充直播间 ID: {room_id}", level="INFO")
                    # 更新配置文件
                    save_config_to_file(room_id, page.login_cookies)
                else:
                    result_text.value += "\n❌ 无法获取直播间 ID，请手动输入！"
            else:
                save_log_to_file("未从 Cookie 中找到 DedeUserID", level="ERROR")
                result_text.value += "\n❌ 未找到用户 ID，无法自动获取直播间 ID！"
            page.update()
            # 清空临时存储的 Cookie 数据
            page.login_cookies = ""

    update_cookies_and_roomid_from_login()

    def get_areas():
        """获取直播分区信息"""
        global areas
        save_log_to_file("正在调用 get_areas() 函数获取直播分区信息", level="INFO")  # 确认函数被调用
        try:
            response = requests.get(
                "https://api.live.bilibili.com/room/v1/Area/getList",
                headers=HEADERS,
            )
            if response.status_code == 200:
                if response.json().get("code") == 0:
                    areas = response.json().get("data", {})
                    save_log_to_file(
                        f"获取直播分区信息成功！分区数据：{json.dumps(response.json(), ensure_ascii=False)}",
                        level="DEBUG",
                    )
                    liveroom_parent_area.options = [
                        ft.dropdown.Option(f"{area['name']}({area['id']})")
                        for area in areas
                    ]
                    save_log_to_file(f"成功设置父分区选项：{len(areas)} 个分区", level="INFO")
                else:
                    save_log_to_file(
                        f"获取直播分区信息失败！错误信息：{response.json().get('message', '未知错误')}",
                        level="ERROR",
                    )
            else:
                save_log_to_file(
                    f"获取直播分区信息失败！错误信息：{response.text}",
                    level="ERROR",
                )
        except requests.exceptions.RequestException as err:
            save_log_to_file(f"网络请求错误：{err}", level="ERROR")
        page.update()

    # 确保调用 get_areas()
    save_log_to_file("初始化主页面，准备调用 get_areas()", level="INFO")
    get_areas()

    # 主页面内容
    main_content = ft.Column(
        scroll=ft.ScrollMode.AUTO,  # 启用列滚动
        expand=True,  # 允许列扩展填满可用空间
        controls=[
            welcome_text,
            result_text,
            ft.Divider(height=20),
            input_row,
            qr_login_row,
            ft.Divider(height=20),
            manage_liveroom_hint_row,
            manage_liveroom_title_row,
            manage_liveroom_tags_row,
            manage_liveroom_area_row,
            ft.Divider(height=20),
            addr_row,
            code_row,
            checkbox_row,
            ft.Divider(height=20),
            button_row,
            ft.Text(value="========== 别拖啦，已经到底啦 ==========", size=14, text_align=ft.TextAlign.CENTER),
            ft.Divider(height=20),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )
    return main_content