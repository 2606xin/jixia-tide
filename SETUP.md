# Jixia Guanlan Automation Setup

This repository contains five GitHub Actions automations for the Jixia Guanlan community lifecycle.

## Required Repository Settings

1. Open **Settings > Actions > General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Enable **Allow GitHub Actions to create and approve pull requests**.

The workflows can use the built-in `GITHUB_TOKEN`. If your organization blocks any required action, create a fine-grained personal access token named `GH_TOKEN`.

## Optional `GH_TOKEN`

Create a repository secret named `GH_TOKEN` with these permissions:

- Contents: read and write
- Pull requests: read and write
- Issues: read and write
- Metadata: read

The workflows use `GH_TOKEN` when present and fall back to `GITHUB_TOKEN`.

## Skill File Format

New skills must be Markdown files under `community/` and must start with YAML frontmatter:

```yaml
---
title: Example Skill
author: your-name
tags:
  - ai
  - workflow
created_at: 2026-05-29
---
```

Optional lifecycle fields such as `updated_at`, `last_used_at`, or `last_interaction_at` are honored by Time Sentinel when deciding whether a skill has been active in the last 180 days.

## Workflows

- **Gatekeeper**: validates pull requests to `main`, comments on failures, and auto-approves plus squash-merges valid skill submissions.
- **Time Sentinel**: runs daily at `00:00 UTC`, moving inactive skills from `community/` to `legacy/`.
- **Influence Sentinel**: runs daily, generating public Skill impact signals in `community/index.json` and `docs/impact.md`.
- **Chronicler**: runs on February 4 at `23:59 UTC`, packages `legacy/` into `Archive_{Year}.zip`, publishes `archive-{year}`, and clears `legacy/`.
- **Resurrection Council**: starts votes from issue comments like `/vote-resurrect skill-name`, then processes completed votes after 7 days.

GitHub cron cannot represent solar terms directly. The Chronicler workflow is scheduled for February 4, which is the usual Lichun date; adjust `.github/workflows/chronicler.yml` if you need a specific year's astronomical timestamp.

## Local Validation

Run the local smoke test suite before pushing workflow changes:

```bash
python scripts/run_local_tests.py
```

The script compiles the automation Python files, parses workflow YAML, and runs the minimal unit tests under `tests/`.

## Contribution Sign-Off

Gatekeeper requires every commit in a pull request to include a Developer Certificate of Origin sign-off.

Use:

```bash
git commit -s -m "Add my skill"
```

See `DCO.md` and `CONTRIBUTING.md` for details.
