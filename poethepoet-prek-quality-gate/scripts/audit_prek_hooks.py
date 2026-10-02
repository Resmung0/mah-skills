#!/usr/bin/env python3
"""Prompt Codex to audit Poe tasks and prek hooks after config edits."""

import json
import sys


CONFIG_NAMES = (
    "prek.toml",
    ".pre-commit-config.yaml",
    ".pre-commit-config.yml",
    "pyproject.toml",
    "poe_tasks.toml",
    "poe_tasks.yaml",
    "poe_tasks.json",
)

POE_TABLE_MARKERS = (
    "[tool.poe",
    '"poe"',
    "tasks:",
)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return 0
    if not isinstance(event, dict):
        return 0

    input_text = "\n".join(strings(event.get("tool_input", {})))
    if not any(name in input_text for name in CONFIG_NAMES) and not any(
        marker in input_text for marker in POE_TABLE_MARKERS
    ):
        return 0

    context = (
        "A Poe task or prek configuration was edited in this task. Inspect the "
        "effective Poe configuration and included task files, then semantically "
        "audit every configured Poe task and every prek hook. For Poe tasks, "
        "review type, command or script, dependencies, group, arguments, "
        "environment, working directory, executor, and public versus internal "
        "use. For hooks, review purpose, command or upstream definition, stage, "
        "file filters, arguments, runtime, and filename behavior. Check overlap "
        "between tasks and hooks, and report concrete findings and recommendations. "
        "Apply changes only within the user's requested scope."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
