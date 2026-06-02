from __future__ import annotations

import argparse
import json

from intent_parser.workflow import DemandWorkflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a B2B sales demand text.")
    parser.add_argument("text", help="Raw sales demand text.")
    args = parser.parse_args()

    result = DemandWorkflow().analyze(args.text)
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
