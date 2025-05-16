# build.ps1
Write-Host "Starting build process..."

# 确保 Python 环境已设置
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found! Please ensure Python is installed."
    exit 1
}

# 设置 UTF-8 编码以避免 Unicode 错误
# 设置 UTF-8 编码以避免 Unicode 错误
$env:PYTHONUTF8 = 1
$env:PYTHONIOENCODING = "utf-8"

# 设置 PowerShell 的输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

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
uv run nuitka --standalone --assume-yes-for-downloads --onefile --windows-icon-from-ico=img\icon.ico --windows-company-name=GamerNoTitle --windows-product-name="B站快速开播及推流码获取工具" --windows-file-version=1.0.0.0 --windows-product-version=1.0.0.0 .\console.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Console build successful! Output as console.exe"
} else {
    Write-Error "Console build failed!"
    exit 1
}

Write-Host "Build process completed."