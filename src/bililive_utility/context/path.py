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