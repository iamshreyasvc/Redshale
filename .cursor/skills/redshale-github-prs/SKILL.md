---
name: redshale-github-prs
description: >-
  GitHub pull request workflow for the Redshale repository (iamshreyasvc/Redshale):
  creating, drafting, editing, and retargeting PRs with the correct merge base. Use
  when the user wants to create or open a PR, run gh pr create, prepare a pull
  request, change PR base branch, or mentions merge base or default branch for
  this project.
---

# Redshale — GitHub pull requests

## Integration branch

- **Default PR base is `dev`**, not `main`. The repository’s default branch on GitHub is **`dev`**.
- When running `gh pr create`, **always** pass `--base dev` unless the user explicitly names another base (e.g. a feature branch).
- When changing an existing PR’s base (`gh pr edit <n> --base …`), use **`dev`** unless the user says otherwise.
- **Do not** assume `main` for this repo’s PR workflow.

## Creating a PR

Follow these steps unless the user specifies a different process.

### 1. Preconditions

- Current branch has the work to merge; commits are pushed to **`origin`** (or the remote the user uses for GitHub).
- `gh` is available and authenticated (`gh auth status`). If not, have the user run `gh auth login`.
- Know the default integration branch: **`dev`**.

### 2. PR title

- Short imperative or summary of the change (under ~72 characters when practical). No trailing period unless it is a full sentence the user supplied verbatim.

### 3. PR description (body)

Before writing the body, scan the diff for anything that warrants optional sections: **database or migrations**, **environment / config examples**, **dependencies** (`package.json`, lockfiles, etc.), **UI changes**, or **manual QA** needs.

Use this **exact section order and headings** for `--body`. **Omit entire sections** that have no real content (do not leave empty headings).

```markdown
## Summary
[1-3 sentences: what this does and why]

## Linear Ticket
ONE-XXXX (use ticket ID format - auto-links in GitHub)

## Changes
[Bullet list of key changes]

## Test Plan
- [ ] [Specific test item based on changes]
- [ ] [Another test item]
- [ ] [Regression check if applicable]

{IF_DATABASE_CHANGES}
## Database Changes
- **Schema**: [List schema modifications]
- **Migrations**: [List migration files if applicable]
{/IF_DATABASE_CHANGES}

{IF_ENV_CHANGES}
## Environment Variables
- **New Variables**: [List new .env variables with descriptions]
{/IF_ENV_CHANGES}

{IF_DEPENDENCY_CHANGES}
## Dependencies
- **New Packages**: [List new packages and their purpose]
{/IF_DEPENDENCY_CHANGES}

{IF_UI_CHANGES}
## Screenshots
[Add screenshots/videos for UI changes]
{/IF_UI_CHANGES}

{IF_NEEDS_MANUAL_QA}
## Test Plan
- [ ] [Manual QA items only - things a human needs to verify]
{/IF_NEEDS_MANUAL_QA}
```

**Template notes**:

- The `{IF_*}` markers are authoring hints only — **do not** include them in the posted PR body. When optional blocks do not apply, omit them entirely.
- The template shows **Test Plan** twice (fixed list vs `{IF_NEEDS_MANUAL_QA}`). In the **submitted** PR, use **one** `## Test Plan` heading and **one** merged checklist of manual QA items (never two `## Test Plan` sections).
- Only include sections that have actual changes or content.
- **Test Plan** is for **manual QA verification only** — never mention automated checks (tests passing, type-check, lint, build). Those are pre-flight gates before opening the PR, not items in the PR body.

**Test plan guidelines**:

- Generate **3–5** specific **manual QA** checkboxes from the actual changes.
- Cover new behavior, and regression for areas that could break.
- Use a **single flat list** (no sub-sections under Test Plan).
- Be specific to the change (not generic placeholders).
- **Skip the Test Plan section** only for trivial changes (e.g. typos, comment-only updates).

**Do not** put any of these in Test Plan: “tests pass”, “type checking passes”, “linting passes”, “build succeeds” — those are not manual QA items.

If there is no Linear ticket, omit the **## Linear Ticket** section or replace with a GitHub issue link if the user provided one.

### 4. Draft vs ready

- Prefer **`--draft`** when the user is still iterating, CI is not green, or they asked for a draft.
- Omit **`--draft`** when the user asked for a ready-for-review PR and the branch is in good shape.

### 5. Create the PR

From the repo root, with the head branch checked out and pushed:

```bash
# Draft (common default while validating)
gh pr create --draft --base dev --title "..." --body "..."

# Ready for review
gh pr create --base dev --title "..." --body "..."
```

If the head branch is not the current branch, pass **`--head owner:branch`** (or **`--head branch`** when appropriate for the fork setup).

### 6. After creation

- Share the PR URL from the command output, or run **`gh pr view --web`** if the user wants the browser.
- For **review standards** (what to check in the diff), see [.cursor/skills/redshale-pr-review/SKILL.md](../redshale-pr-review/SKILL.md).

## Retargeting or editing an existing PR

```bash
gh pr edit <number> --base dev
```

Use other `gh pr edit` flags (title, body) only when the user asks to update those fields.

## Quick reference

```bash
gh pr create --draft --base dev --head <branch> --title "..." --body "..."
gh pr edit <number> --base dev
```
