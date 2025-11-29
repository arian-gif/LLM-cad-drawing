"""Entrypoint for the Prompt → AutoCAD MVP."""

from llm_cad.ui import build_demo


def main() -> None:
    demo = build_demo()
    demo.launch()


if __name__ == "__main__":
    main()
