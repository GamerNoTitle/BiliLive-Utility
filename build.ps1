# build.ps1
Write-Host "Starting build process..."

# 确保 Python 环境已设置
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found! Please ensure Python is installed."
    exit 1
}

# 设置 UTF-8 编码以避免 Unicode 错误
$env:PYTHONUTF8 = 1

# 构建控制台版本 (使用 nuitka 构建 console.py)
Write-Host "Building console executable with Nuitka..."
uv run nuitka --standalone --assume-yes-for-downloads --onefile --windows-icon-from-ico=icon.ico .\console.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Console build successful! Output as console.exe"
} else {
    Write-Error "Console build failed!"
    exit 1
}

# 构建 GUI 版本 (使用 flet build)
Write-Host "Building GUI with Flet..."
uv run flet build windows gui.py --output=gui.build
if ($LASTEXITCODE -eq 0) {
    Write-Host "GUI build successful! Output in gui.build folder."
} else {
    Write-Error "GUI build failed!"
    exit 1
}

Write-Host "Build process completed."