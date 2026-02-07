uv pip install -e .
uv run pyinstaller `
    --name "BiliLive Utility" `
    --windowed `
    --onefile `
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
    --icon="static/favicon.ico" `
    src/bililive_utility/launcher.py