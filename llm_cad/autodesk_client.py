"""Utilities for preparing and (optionally) posting Autodesk payloads."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests

DEFAULT_BASE_URL = "https://developer.api.autodesk.com"
AUTOCAD_ACTIVITY = "/autocad.io/us-east/v2/WorkItems"


def build_request_payload(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap a drawing plan in a minimal Design Automation work-item payload.

    This keeps the MVP narrowly focused: a single activity that receives the
    LLM-produced JSON via the `arguments` block. In production you would reference
    a custom app bundle + activity that consumes this schema.
    """

    return {
        "activityId": "AutoCAD.Activity+prod",
        "arguments": {
            "drawingSpec": {
                "url": "data:application/json," + json.dumps(plan),
                "headers": {"Content-Type": "application/json"},
            }
        },
    }


def maybe_post_to_autodesk(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send the payload when credentials are present; otherwise return a noop."""

    token = os.getenv("AUTODESK_TOKEN")
    base_url = os.getenv("AUTODESK_BASE_URL", DEFAULT_BASE_URL)
    if not token:
        return {
            "sent": False,
            "reason": "AUTODESK_TOKEN missing; showing payload instead of posting",
            "payload": payload,
            "target": base_url + AUTOCAD_ACTIVITY,
        }

    url = base_url.rstrip("/") + AUTOCAD_ACTIVITY
    response = requests.post(url, json=payload, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
    return {"sent": True, "target": url, "response": response.json()}
