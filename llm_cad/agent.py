"""LLM agent wrapper that produces Autodesk-friendly drawing payloads."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency for offline use
    OpenAI = None  # type: ignore

from .prompt import BASE_SYSTEM_PROMPT, tool_schema


@dataclass
class DrawingPlan:
    """Structured output that the UI can render or forward to Autodesk."""

    title: str
    summary: str
    entities: list[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_payload(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "entities": self.entities,
            "metadata": self.metadata,
        }


class DrawingAgent:
    """Lightweight wrapper around the OpenAI client with an offline fallback."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = None
        if self.api_key and OpenAI is not None:
            self.client = OpenAI(api_key=self.api_key)

    def _fallback_plan(self, description: str, metadata: Optional[Dict[str, Any]]) -> DrawingPlan:
        """Produce a deterministic plan when an API key is unavailable.

        The plan keeps the payload schema consistent so the UI and API surfaces
        can be exercised without LLM connectivity.
        """

        return DrawingPlan(
            title="LLM-free sketch",
            summary=f"Prototype layout for: {description[:80]}",
            entities=[
                {
                    "action": "draw_polyline",
                    "layer": "walls",
                    "geometry": {
                        "points": [[0, 0], [5, 0], [5, 3], [0, 3], [0, 0]],
                        "units": metadata.get("units", "meters") if metadata else "meters",
                    },
                    "notes": "Rectangular envelope as a starting frame.",
                },
                {
                    "action": "annotate",
                    "layer": "labels",
                    "geometry": {
                        "location": [1.0, 1.5],
                        "text": description[:60] + ("..." if len(description) > 60 else ""),
                    },
                    "notes": "Drop the prompt in the center as a reminder of intent.",
                },
            ],
            metadata=metadata or {"units": "meters", "format": "dwg"},
        )

    def _llm_plan(self, description: str, metadata: Optional[Dict[str, Any]]) -> Optional[DrawingPlan]:
        """Ask the model to propose a tool call payload."""

        if not self.client:
            return None

        messages = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Create an AutoCAD drawing plan and emit a single tool call."
                    " Include coordinates and layer hints. User request: " + description
                ),
            },
        ]
        tool_choice = {"type": "function", "function": {"name": "create_autocad_drawing"}}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schema(),
                tool_choice=tool_choice,
            )
        except Exception:
            return None

        message = response.choices[0].message
        if not getattr(message, "tool_calls", None):
            return None

        tool_call = message.tool_calls[0]
        arguments = json.loads(tool_call.function.arguments)
        return DrawingPlan(
            title=arguments.get("title", "Autodesk drawing"),
            summary=arguments.get("summary", description),
            entities=arguments.get("entities", []),
            metadata=arguments.get("metadata", metadata or {}),
        )

    def plan(self, description: str, metadata: Optional[Dict[str, Any]] = None) -> DrawingPlan:
        """Return a drawing plan using the LLM when possible, otherwise fallback."""

        return self._llm_plan(description, metadata) or self._fallback_plan(description, metadata)
