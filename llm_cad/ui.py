"""Simple Gradio surface to demo prompt-to-CAD planning."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import gradio as gr

from .agent import DrawingAgent
from .autodesk_client import build_request_payload, maybe_post_to_autodesk


def _format_entities(entities: list[Dict[str, Any]]) -> str:
    return json.dumps(entities, indent=2)


def _format_payload(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2)


def build_demo(agent: Optional[DrawingAgent] = None) -> gr.Blocks:
    agent = agent or DrawingAgent()

    def run(description: str, units: str, file_format: str, send_to_autodesk: bool):
        metadata = {"units": units or "meters", "format": file_format or "dwg"}
        plan = agent.plan(description, metadata)
        payload = build_request_payload(plan.as_payload())
        response = maybe_post_to_autodesk(payload) if send_to_autodesk else None
        return (
            plan.title,
            plan.summary,
            _format_entities(plan.entities),
            _format_payload(payload),
            json.dumps(response, indent=2) if response else "Skipped (preview only)",
        )

    with gr.Blocks(title="Prompt → AutoCAD MVP") as demo:
        gr.Markdown(
            """
            ## Prompt → AutoCAD (MVP)
            Enter a description and optional metadata. If `OPENAI_API_KEY` is configured
            the assistant will make a real tool call; otherwise it falls back to a
            deterministic scaffold so you can test the payload flow.
            """
        )
        with gr.Row():
            description = gr.Textbox(label="What should we draw?", lines=4, placeholder="Rectangular office with two desks")
        with gr.Row():
            units = gr.Textbox(label="Units", value="meters")
            file_format = gr.Textbox(label="File format", value="dwg")
            send_to_autodesk = gr.Checkbox(label="Post to Autodesk (requires AUTODESK_TOKEN)", value=False)

        run_button = gr.Button("Generate plan")

        with gr.Tab("Plan"):
            title_out = gr.Textbox(label="LLM title")
            summary_out = gr.Textbox(label="LLM summary")
            entities_out = gr.Code(label="Entities", language="json")
        with gr.Tab("HTTP payload"):
            payload_out = gr.Code(label="Design Automation payload", language="json")
        with gr.Tab("Submission status"):
            response_out = gr.Code(label="Autodesk response", language="json")

        run_button.click(
            fn=run,
            inputs=[description, units, file_format, send_to_autodesk],
            outputs=[title_out, summary_out, entities_out, payload_out, response_out],
        )

    return demo
