# GitHub Pages 项目主页

本分支 `gh-page` 在仓库根目录提供独立的纯静态项目主页，不需要 Node.js、Python 后端或构建流程。原桌面程序代码未作修改。

## 部署

1. 推送本分支后，打开仓库 **Settings → Pages**。
2. 在 **Build and deployment → Source** 中选择 **Deploy from a branch**。
3. 选择 **gh-page** 分支和 **/ (root)**，然后保存。
4. 等待 GitHub Pages 部署完成，访问：
   https://gamernotitle.github.io/BiliLive-Utility/

这里的分支名是 `gh-page`，不是 `gh-pages`。已添加 `.nojekyll`；样式、脚本和图标均使用相对路径，适用于仓库子路径部署，无需 CDN 或外部字体。

## 本地预览

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

打开 http://127.0.0.1:8765/ 。页面入口为 `index.html`，页面专用样式、脚本和界面预览图在 `assets/`。主页复用桌面程序 `static/` 中的原项目图标和 favicon，但不会加载程序脚本或调用后端。

## 维护

- 下载链接指向 GitHub Releases 的最新发行版，不硬编码版本号或下载文件名。
- 官网沿用 `static/styles.css` 中的粉紫渐变（`#fb7299 → #f093fb`）、白色卡片、灰色渐变卡片头和圆角按钮设计。官网的样式保持独立，避免加载桌面程序专用逻辑。
- `assets/app-preview.png` 由原程序 `static/index.html` 与 `static/styles.css` 在浏览器中渲染生成；禁用程序脚本与外部请求，填入虚构演示数据，字体图标替换为本地符号。它是静态预览图，不是在线控制台，不包含真实账号或密钥。程序 UI 更新后，应重新生成预览图。
- 导航、下载链接、FAQ 在禁用 JavaScript 时仍可使用；脚本仅用于自动更新页脚年份。
- 修改内容时，注意与实际程序能力、发行文件和平台政策保持一致；不要承诺所有账号均可开播。
- 此分支从 `master` 创建并保留项目原有文件；新增主页不会改变桌面应用使用的 `static/index.html`。
