# V4.2 Fallback Protocol

Use this reference only when the active repository does not contain `.project-skills.md`, or when repairing a damaged project constitution.

## Cold Start

1. Use official documentation and suitable general-purpose Skills as the technical baseline.
2. Inspect the repository's core code and existing conventions.
3. Extract one to three rules that are genuinely specific to the project.
4. Initialize `.project-skills.md` with explicit scope, inputs, outputs, and fallback behavior.

Do not turn ordinary language or framework best practices into Project-Specific Skills.

## Per-Turn Dispatch

Every user request triggers a lightweight dispatch:

1. Read the current project constitution.
2. Match relevant registered rules.
3. Select Ascetic, Tidewatcher, or Ranger.
4. Use external technical wisdom when entering an uncovered domain.
5. Execute.
6. Audit whether project-specific reusable logic emerged.

## Profiles

- **Ascetic:** conservative and reproducible; use for high-risk work.
- **Tidewatcher:** balanced default for normal project work.
- **Ranger:** exploratory alternatives only; requires human adoption before persistence.

Priority order:

`legal and security boundaries > active project rules > Ascetic > Tidewatcher > Ranger`

## Evolution Gate

Create a new Project-Specific Skill only when:

- existing project rules cannot cover the behavior; and
- the behavior is complex or likely to recur at least twice; and
- any applicable general Skill has already been used as the foundation; and
- the persisted rule captures a project-specific adaptation.

Audit large completed modules for obsolete, duplicate, or faulty rules.
