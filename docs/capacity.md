# Capacity Boundaries

The Jixia Tide is intentionally built on simple public infrastructure: GitHub, Markdown, Actions, Issues, Releases, and visible rules.

That simplicity is part of the experiment, but it is not infinite. Capacity limits must be public too.

## Current Stage

The project currently runs in **Stage 0**:

- Flat `community/` directory.
- One participant may have at most 5 active Skills.
- Gatekeeper scans active Markdown files to enforce basic rules.
- No external database.
- Repository state is the system state.

This stage is good for starting the experiment, but it should not pretend to scale forever.

## Estimated Capacity

These numbers are planning estimates, not promises.

| Stage | Architecture | Active Skills | Estimated users | Status |
| --- | --- | ---: | ---: | --- |
| 0 | Flat `community/` + simple scans | 0-500 comfortable, 1500 pause threshold | 0-100 comfortable, 300 pause threshold | Current |
| 1 | Registry index + flat directory | Up to around 3000 | Up to around 600 | Future |
| 2 | Author sharding + registry | 10,000-50,000+ | 2,000-10,000+ | Future |
| 3 | Multi-repository / organization-level sharding | 100,000+ | 20,000+ | Future |

The theoretical upper end of this path may reach hundreds of thousands of users only with organization-level governance, indexing, search, anti-abuse work, and probably infrastructure beyond a single repository.

## Capacity Gate

If the project suddenly reaches the current stage's critical threshold, active Skill PRs should pause.

This is not a punishment. It is a public safety valve.

The pause is controlled by `governance/capacity.yml`:

```yaml
status: open
```

or:

```yaml
status: paused
```

When `status` is `paused`, Gatekeeper rejects new or updated active Skill PRs. Governance, documentation, translation, and architecture PRs can still proceed.

## Resume Rule

Skill PRs resume when the community approves the next architecture adjustment.

That adjustment can be proposed by anyone. The project does not assume a central architect. If someone has a better idea, they can bring it to the community.

Possible adjustments include:

- Registry files such as `registry/active-skills.json` and `registry/authors.json`.
- Author-sharded directories such as `community/authors/{author}/`.
- Better search and indexing.
- Multi-repository archival or active-region splitting.

## Why This Exists

The point is not to make the system perfect. The point is to make the limits visible.

If everyone gets stuck at a boundary, that boundary becomes part of the social experiment. The community can decide whether to redesign the system, accept the constraint, or let the project change shape.

People may contribute architecture work, or they may not. Recognition may exist, or it may not. Many people are here just to play, observe, and leave a trace.
