from pathlib import Path
import os

def create_path(path_name):
    """
    Create path_name path if it does not exist
    """
    cwd = Path.cwd()
    dirname = cwd / path_name
    if not dirname.exists():
        print(f"Creating {dirname}")
        os.makedirs(dirname, exist_ok=True)
    return dirname
