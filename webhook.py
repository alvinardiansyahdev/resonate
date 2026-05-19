#!/usr/bin/env python3
"""Minimal GitHub webhook handler — triggers deploy.sh on push to main."""
import hashlib
import hmac
import json
import logging
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

SECRET = os.environ["WEBHOOK_SECRET"].encode()
DEPLOY_SCRIPT = os.path.join(os.path.dirname(__file__), "deploy.sh")
LOG_FILE = "/var/log/resonate-deploy.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


def verify_signature(body: bytes, sig_header: str) -> bool:
    if not sig_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header)


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/webhook/github":
            self._respond(404, "not found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        sig = self.headers.get("X-Hub-Signature-256", "")

        if not verify_signature(body, sig):
            logging.warning("Invalid signature")
            self._respond(403, "forbidden")
            return

        try:
            event = self.headers.get("X-GitHub-Event", "")
            payload = json.loads(body)
            branch = payload.get("ref", "")
        except Exception:
            self._respond(400, "bad payload")
            return

        if event != "push" or branch != "refs/heads/main":
            self._respond(200, "ignored")
            return

        logging.info(f"Push to main by {payload.get('pusher', {}).get('name')} — deploying")
        self._respond(200, "deploying")

        subprocess.Popen(
            ["bash", DEPLOY_SCRIPT],
            stdout=open(LOG_FILE, "a"),
            stderr=subprocess.STDOUT,
        )

    def _respond(self, code: int, msg: str):
        body = msg.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        logging.info(fmt % args)


if __name__ == "__main__":
    port = int(os.environ.get("WEBHOOK_PORT", 9001))
    logging.info(f"Webhook listening on :{port}")
    HTTPServer(("127.0.0.1", port), WebhookHandler).serve_forever()
