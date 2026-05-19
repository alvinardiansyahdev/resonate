import hashlib
import hmac
import logging
import os
import subprocess
from fastapi import APIRouter, Header, HTTPException, Request

router = APIRouter()
logger = logging.getLogger(__name__)

DEPLOY_SCRIPT = os.path.join(os.path.dirname(__file__), "../../deploy.sh")
SECRET = os.environ.get("WEBHOOK_SECRET", "").encode()


def _verify(body: bytes, sig_header: str) -> bool:
    if not SECRET or not sig_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(key=SECRET, msg=body, digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header)


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=""),
    x_github_event: str = Header(default=""),
):
    body = await request.body()

    if not _verify(body, x_hub_signature_256):
        logger.warning("Webhook signature invalid")
        raise HTTPException(status_code=403, detail="invalid signature")

    if x_github_event == "ping":
        return {"ok": True, "msg": "pong"}

    if x_github_event != "push":
        return {"ok": True, "msg": "ignored"}

    import json
    try:
        payload = json.loads(body)
    except Exception:
        raise HTTPException(status_code=400, detail="bad payload")

    if payload.get("ref") != "refs/heads/main":
        return {"ok": True, "msg": "not main branch"}

    pusher = payload.get("pusher", {}).get("name", "unknown")
    commit = payload.get("head_commit", {}).get("message", "")[:60]
    logger.info(f"Deploy triggered by {pusher}: {commit}")

    subprocess.Popen(
        ["bash", os.path.abspath(DEPLOY_SCRIPT)],
        stdout=open("/var/log/resonate-deploy.log", "a"),
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(os.path.abspath(DEPLOY_SCRIPT)),
    )

    return {"ok": True, "msg": f"deploying — {commit}"}
