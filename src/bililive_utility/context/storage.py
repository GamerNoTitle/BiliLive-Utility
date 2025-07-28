from .path import DATA_PATH

def get_content_from_file(filename: str) -> bytes:
    with open(DATA_PATH / filename, "rb") as f:
        return f.read()