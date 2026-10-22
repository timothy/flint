#!/usr/bin/env bash
# Download a model through the running Ollama server. Ollama keeps partial
# downloads, so each retry resumes where the previous attempt stopped.
set -euo pipefail

model=${1:?usage: scripts/pull-model.sh MODEL}
attempts=${PULL_ATTEMPTS:-5}

for ((i = 1; i <= attempts; i++)); do
  if ollama pull "$model"; then
    exit 0
  fi
  if ((i < attempts)); then
    echo "pull attempt $i of $attempts failed; retrying in 15 seconds" >&2
    sleep 15
  fi
done

echo "could not download $model after $attempts attempts" >&2
exit 1
