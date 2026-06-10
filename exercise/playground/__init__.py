import os
from pathlib import Path

# ensure we're running from the top level
# -- base_path=/path/to/playground/..
base_path = Path(__file__).parent.parent
os.chdir(base_path)

from .app import app

# ex02
from ex02.protect import protect_all_routes
protect_all_routes(app)

# ex06
from ex06 import mytools