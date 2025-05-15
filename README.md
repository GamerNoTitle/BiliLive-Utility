# Bililive-Credential-Grabber

这是一个帮助不满足 [B 站新规粉丝数量](https://link.bilibili.com/p/eden/news#/newsdetail?id=4516)的用户开启直播并获取直播凭据的小工具

- Telegram 私信: https://t.me/PaffCreamPMBot  

- Telegram 群组: https://t.me/DohnaNyan  

- Telegram 频道: https://t.me/PaffChannel  

> [!warning]
>
> 温馨提醒：使用本程序开播后别忘了到网页端更改直播的分区，B 站在没有指定直播分区的情况下会自动选择生活区，这可能不是你想要的，所以一定一定一定要记得改掉！！！

## 开箱即用

### 下载程序

访问 https://github.com/GamerNoTitle/Bililive-Credential-Grabber/releases 下载最新的发行版，其中 `gui.zip` 是带有 GUI 界面的工具，而 `console.exe` 是只有命令行的版本，按照自己的需要下载，下面以 `gui.zip` 为例

> [!Tip]
>
> 就我个人而言，我更推荐下载 `gui.zip`，因为它操作更加直观

### 获取登录凭据

访问 B 站的直播页面 [https://link.bilibili.com/p/center/index#/my-room/start-live](https://link.bilibili.com/p/center/index#/my-room/start-live)，完成登录后，按下键盘上的 <kbd>F12</kbd>，然后点击上方的 `网络/Network`，并搜索 `get_user_info`，然后在左边找到任意一条 `get_user_info`（尽量往下找），然后点击它，在右手边往下滑找到 Cookies，复制内容，保留下来，待会要用

![](https://cdn.jsdelivr.net/gh/GamerNoTitle/Bililive-Credential-Grabber@master/img/msedge_TNBFhTIA7i.png)

还是这个页面，我们需要获取我们的直播间 ID，在最顶上直接显示的

![](https://cdn.jsdelivr.net/gh/GamerNoTitle/Bililive-Credential-Grabber@master/img/msedge_YAPXAUPOxR.png)

### 使用程序开播/获取推流码

打开下载的 zip，解压后得到程序，直接打开，在对应的位置输入内容后，点击开播即可

![](https://cdn.jsdelivr.net/gh/GamerNoTitle/Bililive-Credential-Grabber@master/img/flet_N6tYCAz1z0.png)

此时弹出来的地址和密钥就是你的直播凭据，你就可以丢到 OBS 里面愉快地开播了！

> [!warning]
>
> 别忘了到网页端更改直播的分区，B 站在没有指定直播分区的情况下会自动选择生活区，这可能不是你想要的，所以一定一定一定要记得改掉！！！

## 源码启动

推荐使用 uv 来管理本项目，首先你需要 clone 一份源码

```shell
$ git clone https://github.com/GamerNoTitle/Bililive-Identity-Grabber.git
```

然后安装一下环境（需要安装 Python3，我用的是 Python 3.12）

```shell
$ cd Bililive-Identity-Grabber
$ uv sync
```

如果你倾向于用 venv 的话

```shell
$ python -m venv .venv
$ # 如果你是 Linux 用户
$ source .venv/bin/activate
$ # 如果是 Windows 用户
$ .venv\Scripts\activate
$ pip install -r requirements.txt
```

然后直接运行 `python gui.py` 即可

## 赞助

https://bili33.top/sponsors


## 碎碎念

实在是不会做 UI 了，直接用 flet 了（其实是我懒得弄网页控制台了，感觉不是很有必要，又不想用 tkinter）