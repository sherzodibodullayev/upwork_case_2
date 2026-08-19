"""Push workflow JSON to n8n and activate it.

The JSON files in workflows/ are the deliverable — a client imports them straight
into their own n8n. This script is how they get onto a running instance without
clicking through the editor, and how the eval always runs against what is in git
rather than whatever was last edited by hand.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
WORKFLOWS = ROOT / "workflows"
load_dotenv(ROOT / ".env")

URL = os.environ.get("N8N_API_URL", "").rstrip("/")
KEY = os.environ.get("N8N_API_KEY", "")
HEADERS = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json",
           "accept": "application/json"}

# Only these keys may be sent on create/update; n8n rejects the rest as read-only.
WRITABLE = ("name", "nodes", "connections", "settings")


def call(method, path, body=None):
    req = urllib.request.Request(
        URL + path, method=method, headers=HEADERS,
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]


def existing():
    st, body = call("GET", "/api/v1/workflows?limit=100")
    if st != 200:
        sys.exit("cannot list workflows: {} {}".format(st, body))
    return {w["name"]: w["id"] for w in body.get("data", [])}


def deploy(path, activate=True):
    wf = json.loads(Path(path).read_text(encoding="utf-8"))
    payload = {k: wf[k] for k in WRITABLE if k in wf}
    by_name = existing()
    wid = by_name.get(payload["name"])

    if wid:
        st, body = call("PUT", "/api/v1/workflows/" + wid, payload)
        action = "updated"
    else:
        st, body = call("POST", "/api/v1/workflows", payload)
        action = "created"
        wid = body.get("id") if isinstance(body, dict) else None

    if st not in (200, 201):
        print("  {} FAILED {}: {}".format(payload["name"], st, body))
        return None

    if activate:
        ast, abody = call("POST", "/api/v1/workflows/{}/activate".format(wid))
        state = "active" if ast == 200 else "activate failed {} {}".format(ast, abody)
    else:
        call("POST", "/api/v1/workflows/{}/deactivate".format(wid))
        state = "inactive"

    print("  {:34} {:8} {}  id={}".format(payload["name"], action, state, wid))
    return wid


if __name__ == "__main__":
    if not URL or not KEY:
        sys.exit("N8N_API_URL / N8N_API_KEY missing from .env")
    targets = [Path(a) for a in sys.argv[1:] if not a.startswith("-")]
    if not targets:
        targets = sorted(WORKFLOWS.glob("*.json"))
    if not targets:
        sys.exit("no workflow JSON found in " + str(WORKFLOWS))
    print("n8n:", URL)
    for t in targets:
        deploy(t, activate="--inactive" not in sys.argv)
