"""CLI: ingest JSONL telemetry, output sanitized defensive findings."""
from __future__ import annotations

import argparse
import json
import sys
from contextlib import ExitStack
from pathlib import Path
from .core import Guardian, load_policy
from .llm import summarize_local

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Agro AI Guardian — monitor defensivo read-only")
    parser.add_argument("--input", default="-", help="Arquivo JSONL ou - para stdin")
    parser.add_argument("--output", default="-", help="Arquivo JSONL ou - para stdout")
    parser.add_argument("--policy", default="config/policy.example.json")
    parser.add_argument("--local-llm", metavar="MODEL", help="Resumo opcional via Ollama em 127.0.0.1; não decide")
    args = parser.parse_args(argv)
    try:
        guardian = Guardian(load_policy(args.policy))
        with ExitStack() as stack:
            src = sys.stdin if args.input == "-" else stack.enter_context(Path(args.input).open(encoding="utf-8"))
            dst = sys.stdout if args.output == "-" else stack.enter_context(Path(args.output).open("w", encoding="utf-8"))
            for index, raw in enumerate(src, start=1):
                if not raw.strip():
                    continue
                try:
                    data = json.loads(raw)
                    result = guardian.inspect(data)
                    output = result.to_dict()
                    if args.local_llm and result.findings:
                        try:
                            output["local_llm_summary"] = summarize_local(result, args.local_llm)
                        except Exception as exc:
                            output["local_llm_error"] = type(exc).__name__
                    dst.write(json.dumps(output, ensure_ascii=False) + "\n")
                except (ValueError, TypeError, json.JSONDecodeError) as exc:
                    print(f"line {index}: rejected invalid event ({type(exc).__name__})", file=sys.stderr)
                    return 2
        return 0
    except (OSError, ValueError) as exc:
        print(f"Configuration or I/O error: {type(exc).__name__}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
