---
name: poethepoet-prek-quality-gate
description: Decide how development checks should be exposed through Poe the Poet and enforced by prek, and audit configured Poe tasks and prek hooks when changing quality gates.
metadata:
  short-description: Route quality checks through Poe and prek
---

# Poe and prek Quality Gate

Use this skill when adding, changing, or reviewing a development check, a Poe task, or a `prek` hook.

## Workflow

1. Inspect the repository's instructions and current task configuration. Find Poe tasks using Poe's config discovery order: `pyproject.toml` when it contains Poe configuration, otherwise `poe_tasks.toml`, `poe_tasks.yaml`, or `poe_tasks.json`. Follow task includes and nested project configs that contribute tasks. Find the effective `prek` config (`prek.toml`, `.pre-commit-config.yaml`, or `.pre-commit-config.yml`) and respect its precedence. Preserve the project's format, naming, and command conventions.
2. Decide where the check belongs from its lifecycle, runtime, inputs, and intended audience:

   | Placement | Choose it when |
   | --- | --- |
   | Poe task only | Developers or CI need an explicit, reusable command; the check is broad, slow, environment-dependent, mutating, or belongs to test, build, release, or deployment workflows. |
   | `prek` hook only | It is a small, deterministic check tied to a Git event or changed files, and a separate named task would add little value. Prefer built-in or maintained hooks for standard file checks. |
   | Both | The same check should be easy to run on demand and automatically enforced at a suitable Git stage. Reuse the Poe task from a local hook when it accepts the hook's file arguments and remains fast enough for that stage; otherwise keep the hook command focused and avoid duplicating implementation. |

3. Select the lifecycle stage that matches when the invariant matters. Use `pre-commit` for quick staged-file checks, `commit-msg` for message rules, and `pre-push` or CI for broader checks. Use manual Poe tasks for checks that are expensive, need the full project, or should not delay each commit. Do not assume that a hook's `stages` setting installs the corresponding Git hook shim.
4. When a quality-gate task is in scope, inspect **every Poe task** in the effective config and its included task files, plus **every hook** in the effective `prek` config. For each Poe task, understand its type, command or script, dependencies, group, arguments, environment, working directory, executor, and whether it is a public task or an internal helper. For each hook, understand its command or upstream definition, purpose, stage, file filters, arguments, and whether it receives filenames or scans the whole repository. Check for stale, redundant, overlapping, overly broad, unexpectedly slow, or ineffective checks, especially overlap between Poe tasks and hooks. Report concrete findings and recommend scoped changes; edit unrelated entries only when the user's request authorizes the broader cleanup.
5. Implement the selected placement in existing files, keeping one authoritative command where practical. Validate the configuration and run the smallest relevant command or hook. Report the placement decision and any checks that could not be run.

## Coding-Agent Audit Hook

When the user wants this audit to be prompted automatically after a Poe or `prek` config edit, read [references/codex-agent-hook.md](references/codex-agent-hook.md). Codex can run a command hook that detects the edited config and asks the model to inspect every Poe task and `prek` hook. A lifecycle hook is a trigger and context bridge; the model performs the semantic review. Do not describe the command hook itself as an autonomous agent reviewer.
