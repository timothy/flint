#!/usr/bin/env python3
"""Measure Flint's prompt-processing and generation speed through Ollama.

Each run sends a new prompt of roughly N tokens (a unique first line keeps the
prompt cache from helping), caps the reply at --max-tokens, and reports the
timings Ollama measures itself. Flint always reasons, so generated tokens
include its reasoning.
"""
import argparse
import json
import time
import urllib.request
import uuid


def make_prompt(target_tokens):
    # Each generated function is about 20 tokens.
    functions = [
        f"def scale_{i}(x):\n    return x * {i % 97} + {i % 13}\n"
        for i in range(max(1, target_tokens // 20))
    ]
    return (
        f"Run {uuid.uuid4()}.\n"
        + "".join(functions)
        + "\nIn one sentence, what do these functions have in common?"
    )


def generate(url, model, prompt, max_tokens):
    body = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": max_tokens}}
    ).encode()
    request = urllib.request.Request(
        f"{url}/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=3600) as response:
        return json.load(response)


def rate(count, nanoseconds):
    return count / (nanoseconds / 1e9) if nanoseconds else 0.0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="flint:40b-a2b-qat-int4")
    parser.add_argument("--sizes", default="1000,8000,32000", help="approximate prompt sizes in tokens, comma-separated")
    parser.add_argument("--max-tokens", type=int, default=256)
    args = parser.parse_args()

    print(f"{'prompt tokens':>13}  {'prefill tok/s':>13}  {'generated':>9}  {'generate tok/s':>14}  {'wall s':>7}")
    for size in (int(s) for s in args.sizes.split(",")):
        started = time.time()
        result = generate(args.url, args.model, make_prompt(size), args.max_tokens)
        wall = time.time() - started
        prompt_tokens = result.get("prompt_eval_count", 0)
        generated = result.get("eval_count", 0)
        print(
            f"{prompt_tokens:>13}  {rate(prompt_tokens, result.get('prompt_eval_duration', 0)):>13.0f}"
            f"  {generated:>9}  {rate(generated, result.get('eval_duration', 0)):>14.1f}  {wall:>7.1f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
