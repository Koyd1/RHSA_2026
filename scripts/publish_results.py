"""Publish Colab experiment outputs to GitHub using Git Data API.

Usage (Colab):
    from google.colab import userdata
    token = userdata.get("RHSA_GITHUB_TOKEN")
    # after running all experiment cells:
    from scripts.publish_results import publish_results
    publish_results("RHSA_2026_outputs", token)

Never paste the token into a notebook cell or store it in a GitHub file.
"""
from __future__ import annotations
import base64
import os
from pathlib import Path
import requests

REPO = "Koyd1/RHSA_2026"
BRANCH = "main"
ALLOWED_EXTENSIONS = {".csv", ".json", ".png", ".svg", ".pdf", ".txt", ".md"}

def publish_results(output_dir="RHSA_2026_outputs", token=None, repo=REPO, branch=BRANCH):
    """Create an atomic GitHub commit with all supported result files.

    A unique timestamped run directory prevents overwriting prior experiments.
    Each file is uploaded as a blob, then all blobs become one Git commit.
    """
    from datetime import datetime, timezone
    base = Path(output_dir)
    if not base.is_dir():
        raise FileNotFoundError(f"Run the notebook first: {base} does not exist.")
    token = token or os.environ.get("RHSA_GITHUB_TOKEN")
    if not token:
        raise ValueError("Set RHSA_GITHUB_TOKEN in Colab Secrets and explicitly pass it here.")
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    api = f"https://api.github.com/repos/{repo}"
    session = requests.Session()
    session.headers.update(headers)
    def call(method, endpoint, **kwargs):
        response = session.request(method, api + endpoint, timeout=120, **kwargs)
        response.raise_for_status()
        return response.json()
    files = sorted(p for p in base.rglob("*")
                   if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS)
    if not files:
        raise RuntimeError("No eligible result files found.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
    destination = f"results/experiments/{stamp}"
    print(f"Publishing {len(files)} files to {repo}/{branch} under {destination}/")
    ref = call("GET", f"/git/ref/heads/{branch}")
    head_sha = ref["object"]["sha"]
    commit = call("GET", f"/git/commits/{head_sha}")
    base_tree_sha = commit["tree"]["sha"]
    tree_elements = []
    for idx, path in enumerate(files, start=1):
        raw = path.read_bytes()
        if len(raw) > 20_000_000:
            raise ValueError(f"File exceeds 20 MB limit: {path}")
        blob = call("POST", "/git/blobs", json={
            "content": base64.b64encode(raw).decode("ascii"),
            "encoding": "base64"
        })
        relative = path.relative_to(base).as_posix()
        tree_elements.append({
            "path": f"{destination}/{relative}",
            "mode": "100644",
            "type": "blob",
            "sha": blob["sha"]
        })
        if idx % 10 == 0 or idx == len(files):
            print(f"Uploaded {idx}/{len(files)} files")
    tree = call("POST", "/git/trees", json={
        "base_tree": base_tree_sha,
        "tree": tree_elements
    })
    new_commit = call("POST", "/git/commits", json={
        "message": f"Publish RHSA experiment results {stamp}",
        "tree": tree["sha"], "parents": [head_sha]
    })
    call("PATCH", f"/git/refs/heads/{branch}", json={
        "sha": new_commit["sha"], "force": False
    })
    url = f"https://github.com/{repo}/tree/{branch}/{destination}"
    print("Results published:", url)
    return url

if __name__ == "__main__":
    raise SystemExit("Import publish_results and pass your token from Colab Secrets.")
