import os
import sys
import platformdirs

dirs = platformdirs.PlatformDirs(
    appname="BiliLive-Utility",
    appauthor="GamerNoTitle",
    version="v2",
    ensure_exists=True
)
SESSION_PATH = dirs.user_cache_path / "session"
CACHE_PATH = dirs.user_cache_path
DATA_PATH = dirs.user_data_path

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
    return base_path