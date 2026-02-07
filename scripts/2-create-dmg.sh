cd dist
rm -rf "BiliLive Utility"

# Get version from environment variable if available
VOLNAME="BiliLive Utility"
if [ -n "$AG_VERSION" ]; then
  VOLNAME="BiliLive Utility v$AG_VERSION"
fi

create-dmg \
  --volname "$VOLNAME" \
  --volicon "../static/favicon.icns" \
  --window-pos 400 200 \
  --window-size 660 400 \
  --icon-size 100 \
  --icon "BiliLive Utility.app" 160 185 \
  --hide-extension "BiliLive Utility.app" \
  --app-drop-link 500 185 \
  --background "../static/dmg-bg.png" \
  "$VOLNAME.dmg" \
  "."
rm -rf "BiliLive Utility.app"