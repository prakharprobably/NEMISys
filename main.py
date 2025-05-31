from server import create
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDS_PATH = os.path.join(BASE_DIR, 'creds.json')

with open(CREDS_PATH, 'r') as f:
    creds = json.load(f)

app = create(creds["salt"])


port = int(os.environ.get("PORT", 5000))  # fallback for local dev
app.run(host="0.0.0.0", port=port)
