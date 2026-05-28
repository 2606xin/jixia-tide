# Contributing to The Jixia Tide

Languages: [English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

Welcome. This project is an open social experiment about human-AI interaction, not a traditional Skill store.

## Contribution Ground Rules

- Treat every participant as equal.
- Keep rules, disagreements, and governance changes public.
- Do not overwrite or impersonate another author's signed Skill.
- Preserve attribution when quoting, remixing, or extending another Skill.
- Use Issues or PRs to challenge rules, propose changes, and document disagreements.

## Submitting a Skill

Skill submissions must:

- Be Markdown files ending in `.md`.
- Live under `community/`.
- Include YAML frontmatter with `title`, `author`, `tags`, and `created_at`.
- Use `tags` as a YAML list.
- Avoid destructive commands, malicious payloads, or hidden behavior.

Example:

```yaml
---
title: Example Skill
author: your-name
tags:
  - human-ai
  - experiment
created_at: 2026-05-29
---
```

Each participant may have at most 5 active Skills. Gatekeeper counts active Skills in `community/` by the `author` frontmatter field and rejects PRs that would push the same author above the limit.

## Licensing

By contributing, you agree that your contribution is distributed under this project's licenses:

- Code, scripts, workflows: MIT License, see `LICENSE`.
- Documentation and Skill prose: CC BY-SA 4.0, see `LICENSE-DOCS.md`.

## DCO Sign-Off

All commits must include a Developer Certificate of Origin sign-off.

Use:

```bash
git commit -s -m "Add my skill"
```

This adds:

```text
Signed-off-by: Your Name <your.email@example.com>
```

Pull requests without sign-off will be rejected by Gatekeeper.

## Governance Changes

Changes to `CHARTER.md`, lifecycle rules, resurrection thresholds, author rights, or revenue-related rules should be discussed publicly before merging.

The project can evolve. The rules can evolve too. The important part is that the evolution remains visible.
