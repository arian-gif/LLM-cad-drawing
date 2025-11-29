"""Prompt and tool specification for Autodesk-style drawing requests."""

from typing import Dict, List

BASE_SYSTEM_PROMPT = """
You are a CAD automation specialist that plans Autodesk AutoCAD drawings from natural language.
Use tools to propose an HTTP payload the downstream service can send to Autodesk's Design Automation API.
Only request the minimum set of operations to achieve the user's intent.
"""


def tool_schema() -> List[Dict]:
    """Describe the structured tool the LLM should call.

    The schema loosely mirrors what the Autodesk Design Automation HTTP API
    expects so the UI can relay the payload directly.
    """

    return [
        {
            "type": "function",
            "function": {
                "name": "create_autocad_drawing",
                "description": (
                    "Prepare a JSON payload for Autodesk Design Automation that renders"
                    " an AutoCAD drawing based on the user's request."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Drawing title"},
                        "summary": {
                            "type": "string",
                            "description": "Short paragraph describing the drawing",
                        },
                        "entities": {
                            "type": "array",
                            "description": (
                                "Step-by-step drawing primitives with coordinates, units, and"
                                " layer suggestions."
                            ),
                            "items": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "description": "AutoCAD verb"},
                                    "layer": {"type": "string"},
                                    "geometry": {
                                        "type": "object",
                                        "description": "Coordinates or dimensions for the entity",
                                    },
                                    "notes": {"type": "string"},
                                },
                                "required": ["action", "geometry"],
                            },
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Units, scale, file type, and other render options",
                        },
                    },
                    "required": ["title", "summary", "entities"],
                },
            },
        }
    ]
