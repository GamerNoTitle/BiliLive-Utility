uv run nuitka --standalone --assume-yes-for-downloads --onefile --windows-icon-from-ico=icon.ico .\console.py
uv run flet build windows gui.py --output=gui.build