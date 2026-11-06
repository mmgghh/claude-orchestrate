#!/usr/bin/env python3
"""Claude Code Stop hook: reminds you to /clear when the main conversation's context gets large.

Reads the context size from the last main-conversation response in the transcript.
Reminds once when the context crosses CLEAR_REMIND_AT, then again every CLEAR_REMIND_STEP tokens.
"""
import json
import os
import re
import sys
import tempfile

WARN_AT = int(os.environ.get("CLEAR_REMIND_AT", "150000"))
STEP = int(os.environ.get("CLEAR_REMIND_STEP", "40000"))
USAGE_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def context_tokens(transcript_path):
    last_usage = None
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if entry.get("type") != "assistant" or entry.get("isSidechain"):
                    continue
                usage = (entry.get("message") or {}).get("usage")
                if usage:
                    last_usage = usage
    except (OSError, TypeError):
        return 0
    if not last_usage:
        return 0
    return sum(last_usage.get(k) or 0 for k in USAGE_KEYS)


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return
    tokens = context_tokens(data.get("transcript_path"))
    session = re.sub(r"[^A-Za-z0-9_-]", "_", str(data.get("session_id", "default")))
    state_file = os.path.join(tempfile.gettempdir(), "clear-reminder-" + session)

    if tokens < WARN_AT:
        try:
            os.remove(state_file)
        except OSError:
            pass
        return

    try:
        with open(state_file) as f:
            last_warned = int(f.read())
    except (OSError, ValueError):
        last_warned = 0
    if last_warned and last_warned <= tokens < last_warned + STEP:
        return

    try:
        with open(state_file, "w") as f:
            f.write(str(tokens))
    except OSError:
        pass  # can't remember the warning, so it may repeat; still better than failing the hook
    print(json.dumps({
        "systemMessage": (
            f"🧹 Context is ~{tokens // 1000}k tokens. Finish the current task, "
            "make sure the plan file is updated, then /clear and run /orchestrate:run <plan file>."
        )
    }))


if __name__ == "__main__":
    main()
