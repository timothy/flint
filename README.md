# Flint on M4 Max

A local agentic-coding stack for an Apple M4 Max MacBook Pro with 64 GB of unified memory:
[Recursive's Flint](https://recursive.com/updates/introducing-recursive-flint) coding model, served by
[Ollama](https://ollama.com/library/flint) and driven by the [Pi](https://pi.dev) coding agent. Inference runs on
`127.0.0.1`; prompts and code stay on the machine.

The design, diagrams and reasoning are in [docs/flint-on-m4-max.html](docs/flint-on-m4-max.html).

## Why Ollama instead of rec

Recursive's own engine, `rec`, is the faster option, but `rec doctor` (rec 0.1.0) refuses this chip:

```text
rec: Flint requires an Apple M4 Pro, M5 Pro or M5 Max; detected Apple M4 Max
```

Ollama 0.40.8 added Flint on October 21, 2026, and serves Recursive's quantization-trained int4 build as
`flint:40b-a2b-qat-int4`.

## Requirements

- Apple Silicon Mac with at least 48 GB of unified memory
- About 25 GB of free disk for the model weights
- Homebrew, Node.js 22.19+ with npm, and [go-task](https://taskfile.dev) (`brew install go-task`)

## Build

```bash
task
```

`task` runs `task build`, which currently runs `task deps`:

1. Installs the Ollama app (`brew install --cask ollama-app`) and Pi (`@earendil-works/pi-coding-agent`) if they're
   missing.
2. Sets Ollama's server options for this login session: a 131,072-token context, one request at a time and a
   30-minute keep-alive.
3. Starts Ollama and waits for its API on `127.0.0.1:11434`.
4. Downloads the Flint weights (about 22 GB) with `scripts/pull-model.sh`, which resumes and retries interrupted
   downloads.

Each step checks whether it's already done, so running `task` again is quick.

| Task | What it does |
| --- | --- |
| `task deps` | Download the large dependencies: the Ollama app, Pi and the Flint weights |
| `task ollama:config` | Set Ollama's context, parallelism and keep-alive for this login session |
| `task ollama:start` | Start Ollama and wait for its API |
| `task model` | Download only the Flint weights |

`launchctl` settings don't survive a reboot. After restarting the Mac, run `task ollama:config`, then quit and reopen
Ollama.

## What stays out of git

The model weights live in Ollama's store at `~/.ollama/models`, outside this repository. `.gitignore` also excludes
`models/`, weight files (`*.gguf`, `*.safetensors`, `*.bin` and similar), caches, logs and `.env` files, so weights
copied into the repo by hand never end up in a commit.
