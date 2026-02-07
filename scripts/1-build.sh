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
    --osx-bundle-identifier "paff.pesywu.biliutil" \
    --icon="static/favicon.icns" \
    src/bililive_utility/launcher.py

# Sign the application bundle
if [ "$(uname)" == "Darwin" ]; then
    echo "Processing application bundle for ARM64..."
    APP_PATH="dist/BiliLive Utility.app"

    # lean extended attributes
    echo "Files cleanup..."
    xattr -cr "$APP_PATH"

    # Deep sign with entitlements and hardened runtime options
    echo "Signing with hardened runtime..."
    codesign -s - -v -f --deep --options runtime --timestamp --entitlements scripts/entitlements.plist "$APP_PATH"
fi