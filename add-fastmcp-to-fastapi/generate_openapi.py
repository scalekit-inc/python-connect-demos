import json
from pathlib import Path

from todo_api import app

Path(__file__).parent.joinpath("openapi.json").write_text(json.dumps(app.openapi(), indent=2))
print("wrote openapi.json")
