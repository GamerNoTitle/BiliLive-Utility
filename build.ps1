uv pip install -e .
# 读取 toml 文件中的版本号，并替换 src/bililive_utility/utils/version.py 中的版本号
python -c "import toml; version = toml.load('pyproject.toml')['project']['version']; with open('src/bililive_utility/utils/version.py', 'w') as f: f.write(f'__version__ = \"{version}\"')"
uv run pyinstaller `
    --name "BiliLive Utility" `
    --windowed `
    --noconfirm `
    --clean `
    --add-data "static:static" `
    --hidden-import "uvicorn.logging" `
    --hidden-import "uvicorn.loops" `
    --hidden-import "uvicorn.loops.auto" `
    --hidden-import "uvicorn.protocols" `
    --hidden-import "uvicorn.protocols.http" `
    --hidden-import "uvicorn.protocols.http.auto" `
    --hidden-import "uvicorn.protocols.websockets" `
    --hidden-import "uvicorn.protocols.websockets.auto" `
    --hidden-import "uvicorn.lifespan" `
    --hidden-import "uvicorn.lifespan.on" `
    src/bililive_utility/__main__.py