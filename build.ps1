# build.ps1
Write-Host "Starting build process..."

# 确保 Python 环境已设置
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found! Please ensure Python is installed."
    exit 1
}

# 设置 UTF-8 编码以避免 Unicode 错误
$env:PYTHONUTF8 = 1
$pwd = Get-Location

# 构建 GUI 版本
Write-Host "Building GUI with Flet..."
# 尝试使用位置参数指定入口文件
uv run flet build windows --project "Bililive-Credential-Grabber" --product "B站快速开播及推流码获取工具" --company GamerNoTitle --copyright "Copyright (C) 2025 GamerNoTitle" --description "Bililibe-Credential-Grabber is a tool that helps you turn on livestream without using Livehime and get the credential for livestream which is valid in OBS Studio." --cleanup-app --cleanup-packages > flet_build.log 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "GUI build successful! Output in gui.build folder."
} else {
    Write-Error "GUI build failed! Check flet_build.log for details."
    Get-Content -Path flet_build.log -ErrorAction SilentlyContinue
    exit 1
}

# 构建控制台版本
Write-Host "Building console executable with Nuitka..."
uv run nuitka --standalone --assume-yes-for-downloads --onefile --windows-icon-from-ico=img\icon.ico .\console.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Console build successful! Output as console.exe"
} else {
    Write-Error "Console build failed!"
    exit 1
}

Write-Host "Build process completed."
