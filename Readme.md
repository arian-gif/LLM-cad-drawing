# Prompt to CAD Drawing

A minimum-viable demo that turns natural language requests into an Autodesk-ready
AutoCAD payload. The project wraps a lightweight LLM agent with a Gradio UI so
you can preview the structured tool call and (optionally) forward it to Autodesk
Design Automation.

## Getting started

1. Install dependencies (Python 3.10+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Export credentials so the LLM and Autodesk calls can execute:
   ```bash
   export OPENAI_API_KEY=sk-...
   export AUTODESK_TOKEN=eyJhbGciOi...
   # AUTODESK_BASE_URL overrides the default https://developer.api.autodesk.com
   ```
3. Launch the UI:
   ```bash
   python app.py
   ```

Without `OPENAI_API_KEY`, the agent emits a deterministic scaffold so you can
still exercise the payload flow.

## What the UI shows
- **Plan**: The LLM/tool-call output (title, summary, drawing entities).
- **HTTP payload**: A minimal Design Automation work-item request that embeds the
  LLM payload in `arguments.drawingSpec`.
- **Submission status**: A dry-run preview or live POST to Autodesk when
  `AUTODESK_TOKEN` is set.

## Architecture
- `llm_cad/prompt.py` – System prompt + tool schema to steer the LLM into a
  single `create_autocad_drawing` call.
- `llm_cad/agent.py` – Optional OpenAI integration with an offline fallback that
  returns deterministic geometry.
- `llm_cad/autodesk_client.py` – Helper to wrap the LLM plan in a Design
  Automation payload and, when tokens exist, POST it.
- `llm_cad/ui.py` – Gradio Blocks interface wiring the agent to the payload
  helper.
- `app.py` – Entrypoint for local usage.

This is intentionally small so you can swap the agent framework or Autodesk
activity details without reworking the surface.
