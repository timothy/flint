#!/usr/bin/env bash
# Recursive's tool-cycle check: Pi must read a file, write the sum of its two
# integers to result.txt and verify the file with a shell command. Extra
# arguments go to pi, for example --model.
set -euo pipefail

dir=$(mktemp -d "${TMPDIR:-/tmp}/flint-smoke.XXXXXX")
cd "$dir"
printf '19 23\n' > smoke-input.txt

start=$SECONDS
# pi -p can wait on an open stdin, so close it.
pi -p --no-session --mode json "$@" \
  "Read smoke-input.txt with your file-reading tool and add the two integers in it. Write exactly the sum followed by one newline to result.txt. Then run a shell command that fails unless result.txt contains exactly that, and report whether it passed." \
  </dev/null > events.jsonl
elapsed=$((SECONDS - start))

python3 - events.jsonl <<'EOF'
import json, sys
calls = []
for line in open(sys.argv[1], encoding="utf-8"):
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        continue
    if event.get("type") == "tool_execution_start":
        calls.append(event["toolName"])
print(f"tool calls ({len(calls)}): {', '.join(calls) or 'none'}")
EOF

if python3 -c 'from pathlib import Path; raise SystemExit(Path("result.txt").read_bytes() != b"42\n")' 2>/dev/null; then
  echo "PASS in ${elapsed}s (events: $dir/events.jsonl)"
else
  echo "FAIL in ${elapsed}s: result.txt is not exactly 42 and a newline (see $dir)" >&2
  exit 1
fi
