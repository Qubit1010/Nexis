"""Read prospect access tokens from local, gitignored demo records."""
import json
from pathlib import Path

DEMO_RECORDS = Path(__file__).resolve().parents[2] / "quetta-local-market/data/demos"

def demo_token(slug: str) -> str:
    file = DEMO_RECORDS / (slug + ".json")
    if not file.is_file():
        raise RuntimeError("Create the private demo record before this live check: " + slug)
    token = json.loads(file.read_text(encoding="utf-8"))["token"]
    if not isinstance(token, str) or not token:
        raise RuntimeError("Private demo record has no access token: " + slug)
    return token
