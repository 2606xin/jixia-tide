---
name: origin-secure-skill
description: Persistent project-specific Skill architecture and per-turn dispatch for repositories using .project-skills.md. Use for every coding, documentation, testing, review, planning, architecture, governance, or maintenance request in a repository that contains .project-skills.md. Also use when creating, updating, auditing, routing, deprecating, or circuit-breaking Project-Specific Skills, when project instructions must survive long or new conversations, or when recurring project logic should be persisted instead of remaining a one-off prompt.
---

# Origin Secure Skill

Treat `.project-skills.md` in the active repository as the project constitution.

## Per-Turn Hook

For every user request in a repository containing `.project-skills.md`:

1. Read `.project-skills.md` before planning or editing.
2. Identify the active Project-Specific Skills relevant to the request.
3. Inspect the current branch, repository state, and affected files when the task depends on them.
4. Select the decision profile:
   - Use **Ascetic** for security, law, permissions, automatic merging, migrations, destructive operations, and core governance.
   - Use **Tidewatcher** by default for ordinary engineering and documentation.
   - Use **Ranger** only for explicitly requested exploration, naming, narrative, or alternative ideas. Never let Ranger silently replace the stable plan.
5. Use an official or general-purpose Skill first when entering a new technical domain not covered by the project constitution.
6. Execute the task.
7. Before finishing, decide whether the work created reusable project-specific logic, exposed an obsolete rule, or triggered a circuit breaker.

Do not create or update a Project-Specific Skill unless both are true:

- Existing Project-Specific Skills do not adequately cover the behavior.
- The behavior is high-complexity or expected to recur at least twice.

If a general Skill was used, persist only the project-specific adaptation, not generic best practices.

## Persistence

When the threshold is met:

1. Prefer updating an existing Project-Specific Skill over adding a near-duplicate.
2. Name new entries `Project-Specific-[Module]-[Function]`.
3. Record status, scope, inputs, expected outputs, and fallback behavior.
4. Append or update the entry in `.project-skills.md` immediately.
5. Keep changes auditable and narrowly scoped.

When a registered rule causes an error:

1. Stop relying on it for the current task.
2. Fall back to general best practice or basic logic.
3. Mark it with the project's abnormal or needs-repair status and record the reason.
4. Do not reactivate it without an explicit repair.

## Stable Decisions

Do not promise identical prose across runs. Stabilize governance decisions using:

- repository name and structure;
- current branch and recent commit;
- current `.project-skills.md`;
- the current user request;
- prior similar decisions visible in the repository.

Keep decisions stable about whether to create, update, deprecate, or circuit-break a Skill. Allow wording and implementation details to vary when the constitution permits.

## Fallback

If `.project-skills.md` is absent, use official/general Skills as the baseline and inspect the project before initializing one. Read [references/protocol.md](references/protocol.md) for the cold-start and V4.2 fallback rules.

Do not create a project constitution for trivial or self-contained requests.
