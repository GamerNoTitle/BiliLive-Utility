import git
from datetime import datetime
from pydantic import BaseModel

BUILD_TIME = "__BUILD_TIME__"

def get_git_short_hash_from_library() -> str | None:
    """
    使用 GitPython 库获取当前 Git 仓库的短哈希值。

    Returns:
        str: 短哈希值，如果失败则返回 None。
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        
        head_commit = repo.head.commit

        return "dev-" + head_commit.hexsha[:7] 

    except git.InvalidGitRepositoryError:
        return None
    except Exception as e:
        return None

class Version(BaseModel):
    """
    版本信息模型。
    """
    version: str
    build: str

VERSION = Version(
    version=get_git_short_hash_from_library() or "__version__",
    build=BUILD_TIME if BUILD_TIME != "__BUILD_TIME__" else "dev-" + str(datetime.utcnow().isoformat())
)