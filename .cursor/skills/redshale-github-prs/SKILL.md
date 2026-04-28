---
name: redshale-github-prs
description: >-
  GitHub pull request conventions for the Redshale repository (iamshreyasvc/Redshale).
  Use when creating, editing, or retargeting PRs, or when the user mentions merge base
  or default branch for this project.
---

# Redshale — GitHub pull requests

## Integration branch

- **Default PR base is `dev`**, not `main`. The repository’s default branch on GitHub is **`dev`**.
- When running `gh pr create`, **always** pass `--base dev` unless the user explicitly names another base (e.g. a feature branch).
- When changing an existing PR’s base (`gh pr edit <n> --base …`), use **`dev`** unless the user says otherwise.
- **Do not** assume `main` for this repo’s PR workflow.

## Quick reference

```bash
gh pr create --draft --base dev --head <branch> --title "..." --body "..."
gh pr edit <number> --base dev
```
