---
name: commit-grouping
description: Analyze staged files, group them into logically related sets (by CODEOWNERS, top-level path, or file type), and produce one conventional-commit-style message per group. If staged files appear to belong to multiple logical changes, suggest separating them into multiple commits and provide the git commands needed to create each commit. This skill should be used when the user wants to commit staged changes for the project's remote repository.
---

# Commit Grouping Skill

## When to Use
- You have staged files and want to ensure commits are focused and follow Conventional Commits.
- You want automated grouping hints and validated commit messages before committing.

## Inputs
- The repository working tree with staged files (`git add` already applied).
- Optional `CODEOWNERS` file at `.github/CODEOWNERS` or `CODEOWNERS` for owner-based grouping.
- The `poe` task `validate-commit` defined in `poe_tasks.toml` (this skill calls it to validate messages).

## Outputs
- A human-readable report of groups: owner/scope, file list, suggested conventional commit message.
- Validation result for each suggested message (pass/fail) including `cz check` output.
- A suggested sequence of shell commands to create one commit per group (non-destructive sequence using staging/unstaging).

## Workflow (Step-by-step)
1. Gather staged files:
   - Run: `git diff --name-only --staged`
   - If no files are staged, return: "No staged files found." and stop.

2. Determine grouping strategy (priority order):
   - If `CODEOWNERS` exists, parse it and map files to the longest-matching pattern owner.
   - Otherwise, group by top-level path segment (first directory name) as the default scope.
   - Optionally, for mixed-language changes, also consider file-type heuristics to refine the change-type (e.g., `docs`, `test`, `feat`).

3. For each group produce a suggested message:
   - Heuristics to decide Conventional Commit `type`:
     - `docs`: files under `docs/` or with `.md`
     - `test`: files under `tests/` or filenames containing `test_`
     - `fix`: presence of changes in code files and references to bug fixes (manual signal)
     - `feat`: additions of new source files or feature-flagged code
     - fallback: `chore`
   - Compose `scope` from CODEOWNERS entry (if available) or the top-level directory.
   - Example: `feat(parser): add support for new pipeline operators`

4. Validate each suggested message using the project's `poe` task:
   - Run: `uv run poe validate-commit --message "<suggested message>"`
   - If validation fails, attempt a minimal repair:
     - Ensure a valid `type` is present (one of the conventional types in the project's pattern).
     - Add or adjust a `scope` or change the `type` to `chore` if unsure.
   - If automatic repair cannot produce a valid message, present the failing output and ask for human edit.

5. If multiple groups exist, produce safe commands to create separate commits (non-destructive):
   - Save staged file lists for each group to temporary files.
   - Unstage everything: `git restore --staged .`
   - For each group:
     - `git add $(cat /tmp/group-N-files.txt)`
     - `git commit -m "<validated message>"`
   - Re-stage any remaining files if needed.

   Example (shell sketch):

   ```bash
   git diff --name-only --staged > /tmp/all-staged.txt
   # create files /tmp/group-1.txt /tmp/group-2.txt with the files for each group
   git restore --staged .
   git add $(cat /tmp/group-1.txt) && git commit -m "feat(parser): add support for X"
   git add $(cat /tmp/group-2.txt) && git commit -m "docs(readme): update usage"
   # optionally re-stage other files
   git add $(cat /tmp/other.txt)
   ```

6. Present final output:
   - For each group: scope, files, suggested message, validation output, and the exact `git` commands to run.

## Decision Points & Branching
- If `CODEOWNERS` maps files to multiple owners within a single logical change, the skill should still prefer grouping by logical path (e.g., `src/parser/*`) and surface owners as metadata.
- If a suggested commit message fails validation after two automated repair attempts, halt and request a human-provided message.
- Prefer smaller, focused commits; if a group contains > 40 files, mark it as "Large change" and recommend manual review or splitting by sub-scope.

## Quality Criteria / Completion Checks
- Every suggested message must pass `poe validation.validate-commit`.
- Every suggested commit should include at least one file and a non-empty subject line.
- The skill should not run `git commit` automatically without explicit user approval.

## Example Prompts for the Agent
- "Analyze staged files and propose conventional commit(s)."
- "Group staged files by CODEOWNERS and suggest validated commit messages."
- "Split the staged files into logical commits and show the git commands to run."

## Failure Modes
- Missing `poe` or `cz` in environment: return a clear error indicating the missing tool.
- No staged files: short-circuit with a helpful message.
- Ambiguous grouping: present multiple grouping options and ask the user to choose.

## Implementation Notes for Developers
- Parse `CODEOWNERS` by longest pattern match.
- Use conservative heuristics for `type` inference; prefer `chore` over wrong `feat`/`fix`.
- Keep the skill idempotent and non-destructive; do not run commits unless explicitly asked.

