"""Explicit CPU/mock demonstration only; never falls back from a real model."""

import argparse
from pathlib import Path

from .agent import Agent
from .contracts import AgentError, ImageInput, Method, load_limits
from .mock_adapter import MockAdapter
from .reporting import to_json, to_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", required=True, choices=["mock"])
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--method", required=True, choices=[m.value for m in Method])
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    try:
        agent = Agent(load_limits(args.config), MockAdapter())
        report = agent.run(ImageInput(args.input_id, args.image), Method(args.method))
        print(to_json(report) if args.format == "json" else to_markdown(report))
        if report.status != "complete":
            raise SystemExit(2)
    except AgentError as exc:
        parser.exit(2, f"Refused: {exc.code}\n")


if __name__ == "__main__":
    main()
