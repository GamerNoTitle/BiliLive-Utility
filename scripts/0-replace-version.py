import tomllib
import os
from pathlib import Path

# Read version
version = os.environ.get("AG_VERSION")

if not version:
    print("Version not provided in env AG_VERSION, reading from pyproject.toml...")
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        version = data["project"]["version"]
        print(f"Found version from toml: {version}")
        
        # Set output only if we read it from source
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print(f"version={version}", file=fh)
                
    except Exception as e:
        print(f"Error reading pyproject.toml: {e}")
        exit(1)
else:
    print(f"Using version from env: {version}")

# Update version
target_file = Path("src/bililive_utility/utils/version.py")
if target_file.exists():
    content = target_file.read_text(encoding="utf-8")
    new_content = content.replace('"__version__"', f'"{version}"')
    
    if content != new_content:
        target_file.write_text(new_content, encoding="utf-8")
        print(f"Updated {target_file}")
    else:
        print(f"Warning: Placeholder '__version__' not found in {target_file}")
else:
    print(f"Error: {target_file} not found")
    exit(1)
