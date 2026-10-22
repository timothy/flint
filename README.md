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
`flint:40b-a2b-qat-int4` on its MLX runner.

## Requirements

- Apple Silicon Mac with at least 48 GB of unified memory
- About 25 GB of free disk for the model weights
- Homebrew, Node.js 22.19+ with npm, `jq` (included in macOS 15 and later), and [go-task](https://taskfile.dev)
  (`brew install go-task`)

## Build

```bash
task
```

`task` runs `task build`:

1. **Tools.** Installs the Ollama app (`brew install --cask ollama-app`) and Pi (`@earendil-works/pi-coding-agent`)
   if they're missing.
2. **Ollama settings.** Sets a 131,072-token context, one request at a time and a 30-minute keep-alive for this login
   session.
3. **Start.** Starts Ollama and waits for its API on `127.0.0.1:11434`.
4. **Model.** Downloads the Flint weights (about 22 GB) with `scripts/pull-model.sh`, which resumes and retries
   interrupted downloads.
5. **Pi.** Makes Flint Pi's default model with a 131,072-token window and a 32,768-token output budget, and removes
   the web-search extension that Ollama's launcher installs.

Steps 1 to 4 are `task deps`, the task that downloads the large dependencies. Each step checks whether it's already
done, so running `task` again is quick.

Then check the setup and start coding:

```bash
task smoke
cd ~/apps/your-repo
pi
```

| Task | What it does |
| --- | --- |
| `task deps` | Download the large dependencies: the Ollama app, Pi and the Flint weights |
| `task pi:config` | Point Pi at Flint with the planned limits and no web-search extension |
| `task smoke` | Run Recursive's tool-cycle check in a throwaway folder |
| `task bench` | Measure prompt and generation speed, for example `task bench -- --sizes 1000,32000` |
| `task ollama:config` | Set Ollama's context, parallelism and keep-alive for this login session |
| `task ollama:start` | Start Ollama and wait for its API |
| `task model` | Download only the Flint weights |

`launchctl` settings don't survive a reboot. After restarting the Mac, run `task ollama:config`, then quit and reopen
Ollama.

Start Pi with `pi`, not `ollama launch pi`. The launcher rewrites Pi's config and installs the web-search extension
again; if you use it, run `task pi:config` afterwards.

## Measured on this Mac

October 22, 2026, with Ollama 0.40.8, `flint:40b-a2b-qat-int4` and Pi 1.4.0. From
`task bench -- --sizes 1000,8000,32000,100000`, each prompt new to the cache and each reply capped at 256 tokens:

| Prompt tokens | Prefill tok/s | Generate tok/s | Wall time |
| ---: | ---: | ---: | ---: |
| 840 | 1,864 | 139.8 | 2.4 s |
| 6,439 | 1,746 | 130.5 | 5.7 s |
| 26,242 | 1,189 | 114.0 | 24.4 s |
| 84,039 | 662 | 62.3 | 131.3 s |

Ollama reported 28 GB in use after the largest prompt. `task smoke` passed in 8 seconds. Pi's own prompt is about
1,460 tokens, and later turns in a session reused it from the KV cache instead of processing it again.

## Known issues

- **`pi -p` can wait on an open stdin.** In JSON mode it sat for more than 10 minutes without contacting the model
  until stdin was redirected from `/dev/null`. The scripts here redirect it; do the same in your own scripts.
- **Trailing newlines can go missing from tool arguments.** In one run Flint sent Pi's `write` tool `"42"` instead of
  `"42\n"` six times before falling back to `printf` in bash. Expect files written with `write` to lack a final
  newline, and look twice at exact-text `edit` calls that end in one.
- **`ollama launch pi --config` needs an interactive terminal**, even with `--model`. `task pi:config` works around
  it.

## What stays out of git

The model weights live in Ollama's store at `~/.ollama/models`, outside this repository. `.gitignore` also excludes
`models/`, weight files (`*.gguf`, `*.safetensors`, `*.bin` and similar), caches, logs and `.env` files, so weights
copied into the repo by hand never end up in a commit.
