Write-Host "Starting build process..."

# 确保 Python 环境已设置
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found! Please ensure Python is installed."
    exit 1
}

# 设置 UTF-8 编码以避免 Unicode 错误
$env:PYTHONUTF8 = 1
$env:PYTHONIOENCODING = "utf-8"

# 设置 PowerShell 的输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 调试编码信息
Write-Host "Current Output Encoding: $([Console]::OutputEncoding)"
Write-Host "Current Input Encoding: $([Console]::InputEncoding)"

# 构建 GUI 版本
Write-Host "Building GUI with Flet..."
# 定义参数，暂时避免中文
$projectName = "BiliLive-Utility"
$productName = "Bililive Utility"
$companyName = "GamerNoTitle"
$copyrightInfo = "Copyright (C) 2025 GamerNoTitle"
$description = "Bililibe Utility is a tool that helps you turn on livestream without using Livehime and get the credential for livestream which is valid in OBS Studio."

# 构建控制台版本
Write-Host "Building console executable with Nuitka..."

# 使用 flet build 命令
uv run flet build windows --project "$projectName" --product "$productName" --company "$companyName" --copyright "$copyrightInfo" --description "$description" --cleanup-app --cleanup-packages > flet_build.log 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "GUI build successful! Output in gui.build folder."
} else {
    Write-Error "GUI build failed! Check flet_build.log for details."
    Get-Content -Path flet_build.log -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Build process completed."