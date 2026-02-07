uv pip install -e .
uv run pyinstaller \
    --name "BiliLive Utility" \
    --windowed \
    --onedir \
    --noconfirm \
    --clean \
    --add-data "static:static" \
    --hidden-import "uvicorn.logging" \
    --hidden-import "uvicorn.loops" \
    --hidden-import "uvicorn.loops.auto" \
    --hidden-import "uvicorn.protocols" \
    --hidden-import "uvicorn.protocols.http" \
    --hidden-import "uvicorn.protocols.http.auto" \
    --hidden-import "uvicorn.protocols.websockets" \
    --hidden-import "uvicorn.protocols.websockets.auto" \
    --hidden-import "uvicorn.lifespan" \
    --hidden-import "uvicorn.lifespan.on" \
    --icon="static/favicon.icns" \
    src/bililive_utility/launcher.py

# Sign the application bundle
if [ "$(uname)" == "Darwin" ]; then
    echo "Signing application bundle..."
    codesign -s - -v -f --deep --entitlements scripts/entitlements.plist "dist/BiliLive Utility.app"
fi