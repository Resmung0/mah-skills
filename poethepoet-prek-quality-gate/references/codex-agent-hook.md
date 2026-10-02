# Codex Hook for Reviewing Poe and `prek` Changes

Codex lifecycle hooks support `command` and `mcp_tool` handlers. Although `agent` handlers are parsed, Codex currently skips them. A command hook can detect a `prek` config edit and return `additionalContext`; Codex then performs the semantic audit as part of its turn.

The bundled `scripts/audit_prek_hooks.py` uses only the Python standard library. Add a `PostToolUse` handler to the desired Codex hook layer (`~/.codex/hooks.json`, `~/.codex/config.toml`, or a trusted project's `.codex/` layer):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "apply_patch|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.codex/skills/poethepoet-prek-quality-gate/scripts/audit_prek_hooks.py",
            "statusMessage": "Preparing quality gate audit"
          }
        ]
      }
    ]
  }
}
```

The script stays silent for unrelated edits. It triggers for `prek.toml`, `.pre-commit-config.yaml`, `.pre-commit-config.yml`, `pyproject.toml`, `poe_tasks.toml`, `poe_tasks.yaml`, or `poe_tasks.json`, and for tool input that looks like a Poe task table. It asks Codex to inspect the effective Poe config and included task files, then review every configured Poe task and `prek` hook. The hook does not parse task or hook semantics, run Poe, or block the completed edit.

Merge the handler into the existing hook file instead of replacing other entries. Review and trust the changed hook definition in Codex (`/hooks`) before relying on it. Project-level hooks run only for trusted `.codex/` layers. This trigger is Codex-specific; other coding agents need their own lifecycle hook mechanism, but can follow the same audit criteria in `SKILL.md`.

Codex hook events and output formats can change. Check the current [Codex Hooks documentation](https://developers.openai.com/codex/hooks) before adapting this integration.
