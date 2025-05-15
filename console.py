import requests
import os
import json
from datetime import datetime

def parse_cookie_string(cookie_string):
    """将 Cookie 字符串解析为字典形式"""
    cookie_dict = {}
    if not cookie_string:
        return cookie_dict
    # 分割 Cookie 字符串为多个键值对
    pairs = cookie_string.split(";")
    for pair in pairs:
        pair = pair.strip()
        if "=" in pair:
            key, value = pair.split("=", 1)  # 使用 split('=', 1) 避免分割值中的 '='
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
    print(f"推流信息已保存到文件: {filename}")

def main():
    welcome_art = """
    ╔══════════════════════════════════════════════╗
    ║        Bilibili 直播开播及凭据获取工具       ║
    ╚══════════════════════════════════════════════╝
                  Made by GamerNoTitle
            (https://github.com/GamerNoTitle)
                  最后更新：2025/5/15
    ----------------------------------------------
      本工具可帮助你快速获取推流地址和密钥，用于开播。
    ----------------------------------------------
    """
    print(welcome_art)

    # 获取直播间号
    roomid = input("请输入你的直播间号：")
    if not roomid.strip():
        print("错误：直播间号不能为空！")
        os._exit(1)

    # 获取 Cookie
    print("\n请按照以下步骤获取 Cookies：")
    print("1. 打开浏览器，登录B站，访问 https://link.bilibili.com/p/center/index#/my-room/start-live")
    print("2. 按 F12 打开开发者工具")
    print("3. 点击上方 Network/网络，搜索 'get_user_info'")
    print("4. 点开一条记录，在右侧 Headers/请求标头 找到 Cookies，复制完整字符串")
    print("5. 直接粘贴到下方")
    cookie_string = input("\n请输入你的 Cookies：")
    if not cookie_string.strip():
        print("错误：Cookies 不能为空！")
        input("按下回车键退出...")
        os._exit(1)

    # 解析 Cookie 字符串为字典
    cookies = parse_cookie_string(cookie_string)
    if not cookies:
        print("错误：解析 Cookies 失败，请检查是否正确复制！")
        input("按下回车键退出...")
        os._exit(1)

    # 提取 csrf (bili_jct)
    csrf = cookies.get("bili_jct")
    if not csrf:
        print("错误：未找到 bili_jct，请检查 Cookies 是否完整或正确！")
        print("请按照以下步骤重新获取：")
        print("1. 打开浏览器，登录B站，访问 https://link.bilibili.com/p/center/index#/my-room/start-live")
        print("2. 按 F12 打开开发者工具")
        print("3. 点击上方 Network/网络，搜索 'get_user_info'")
        print("4. 点开一条记录，在右侧 Headers/请求标头 找到 Cookies，复制完整字符串")
        print("5. 直接粘贴到下方")
        input("按下回车键退出...")
        os._exit(1)

    # 请求头
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://link.bilibili.com",
        "priority": "u=1, i",
        "referer": "https://link.bilibili.com/p/center/index",
        "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    }

    # 请求数据
    start_body = {
        "room_id": roomid,
        "platform": "pc_link",
        "area_v2": "624",
        "backup_stream": "0",
        "csrf_token": csrf,
        "csrf": csrf,
    }

    stop_body = {
        "room_id": roomid,
        "platform": "pc_link",
        "csrf_token": csrf,
        "csrf": csrf,
    }

    try:
        # 发送开播请求
        print("\n正在发送开播请求...")
        start_resp = requests.post(
            "https://api.live.bilibili.com/room/v1/Room/startLive",
            cookies=cookies,
            headers=headers,
            data=start_body,
        ).json()
        print("开播响应:", json.dumps(start_resp, indent=2, ensure_ascii=False))

        # 检查开播是否成功
        if start_resp.get("code") == 0:
            print("\n🎉 开播成功！推流信息如下：")
            rtmp_data = start_resp.get("data", {}).get("rtmp", {})
            addr = rtmp_data.get("addr", "❌ 找不到推流地址！")
            code = rtmp_data.get("code", "❌ 找不到推流密钥！")
            print(f"推流地址：{addr}")
            print(f"推流密钥（推流码）：{code}")

            # 保存推流信息到文件
            save_stream_info(roomid, addr, code)
        else:
            print(f"\n❌ 开播失败！错误信息：{start_resp.get('message', '未知错误')}")
            return

        # 询问是否需要立即停播
        stop_choice = input("\n是否需要立即停播？(y/n，默认 n)：").strip().lower()
        if stop_choice == "y":
            print("\n正在发送停播请求...")
            stop_resp = requests.post(
                "https://api.live.bilibili.com/room/v1/Room/stopLive",
                cookies=cookies,
                headers=headers,
                data=stop_body,
            ).json()
            print("停播响应:", json.dumps(stop_resp, indent=2, ensure_ascii=False))
            if stop_resp.get("code") == 0:
                print("\n🎉 停播成功！")
            else:
                print(f"\n❌ 停播失败！错误信息：{stop_resp.get('message', '未知错误')}")
        else:
            print("\n未执行停播操作，可稍后手动停播。")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求错误：{e}")
        print("请检查网络连接或 Cookies 是否有效（可能已过期）。")
    except Exception as e:
        print(f"\n❌ 发生未知错误：{e}")
        print("请检查输入信息或稍后重试。")

if __name__ == "__main__":
    main()
    input("\n按 Enter 键退出...")