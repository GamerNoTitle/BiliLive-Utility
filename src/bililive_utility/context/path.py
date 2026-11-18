import os
import sys
import platformdirs

# 只声明路径，不在导入时创建任何目录：
# 程序只用到缓存目录，且在真正写文件时才按需 mkdir，避免在用户磁盘上留下空壳目录。
dirs = platformdirs.PlatformDirs(
    appname="BiliLive-Utility",
    appauthor="GamerNoTitle",
)

CACHE_PATH = dirs.user_cache_path
SESSION_PATH = CACHE_PATH / "session"

# 旧版本曾在应用目录后再追加一个版本段（version="v2"），路径形如
#   ~/Library/Caches/BiliLive-Utility/v2/session
# 这个常量只用于「只读回退」：新路径没有文件时，去旧路径读一次，
# 以保证老用户不必重新扫码登录。程序不会迁移、改写或删除旧目录里的任何内容，
# 是否清理旧目录由用户自行决定。
LEGACY_CACHE_PATH = CACHE_PATH / "v2"


def get_resource_path() -> str:
    """
    获取资源文件的绝对路径，兼容开发环境和打包环境。
    """
    if getattr(sys, 'frozen', False):
        # 打包环境
        base_path = os.path.abspath(sys._MEIPASS)
    else:
        # 开发环境
        base_path = os.path.abspath(".")
    print(f"Resource base path: {base_path}")
    return base_path
