cd dist
hdiutil create -volname "BiliLive Utility" -srcfolder . -ov -format UDBZ "./BiliLive Utility.dmg"
rm -rf "BiliLive Utility.app"