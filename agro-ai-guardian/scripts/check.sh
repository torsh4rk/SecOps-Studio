#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
python3 -m agro_guardian --policy config/policy.example.json --input examples/events.jsonl
