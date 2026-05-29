# The Jixia Tide Charter

Languages: [Simplified Chinese](CHARTER.md) | [English](CHARTER.en.md) | [i18n Guide](docs/i18n.md)

The original text is in Chinese. If translation causes semantic misunderstanding, please help maintain and correct it through Issues or PRs.

## 0. Purpose

The Jixia Tide is not a traditional Skill store or product catalog. It is an open experiment about reciprocal thought, everyday social research, and the boundaries between humanity and machine intelligence.

This charter turns the spirit of the README into public, discussable, and executable rules.

## 1. Fundamental Principles

1. **Equal Participation**
   Founders, contributors, and later participants have no natural hierarchy. The founder represents a historical starting point, not permanent authority.

2. **Code as Law, Rules as Changeable**
   The community prefers public scripts, public rules, and GitHub-native records. Every rule can be challenged and changed through visible process.

3. **Public Design, Not Hidden Control**
   Governance is often just simple scripts and limited dimensions. Its flaws are acknowledged. Being broken by reality is also part of the experiment.

4. **Time as Witness**
   Core rules should not be rewritten in haste. Important changes should move slowly enough to be seen and discussed.

5. **No Permanent Death Sentence**
   A Skill can sleep, move to legacy, or be archived, but it should not permanently lose the right to be rediscovered and resurrected.

6. **Stability Without Sacrificing Equality**
   Security fixes, legal-risk handling, and abuse prevention should protect service continuity and participant experience without turning the project into hidden privilege or arbitrary rule by a few people.

## 2. Participants and Founder

Anyone may submit, discuss, question, remix, or improve project rules. No participant receives priority because of identity, fame, seniority, or technical status.

The founder has no real privilege. If anything remains, it is historical attribution: someone once lit a lamp here. Power, rules, and possible revenue belong to public rules, community consensus, and time.

## 3. Skill Submission Rules

Skills must:

- Be `.md` files.
- Live under `community/`.
- Include YAML frontmatter.
- Include at least `title`, `author`, `tags`, and `created_at`.
- Use a YAML list for `tags`.
- Include DCO `Signed-off-by` in every commit.

This project uses a dual-license structure:

- Code, scripts, and workflows use the MIT License.
- Documentation, charter text, project prose, and Skill text use CC BY-SA 4.0.

Each participant may have at most 5 active Skills. Gatekeeper counts active Skills in `community/` by the `author` frontmatter field and rejects PRs that would push the same author above the limit.

## 4. Authorship and Remixing

Signed Skill text carries personal expression and history. By default, others should not directly rewrite it.

To evolve another person's Skill:

- Open an Issue with a proposal.
- Create a derivative Skill and preserve attribution.
- Wait for the original author to revise it.

Malicious overwriting, deletion, or impersonation is prohibited.

Except for signed Skill text and its authorship history, project code, documents, rules, and automation can be discussed and changed through public PRs.

## 5. Automation

### Gatekeeper

Gatekeeper validates PRs, checks required metadata, scans obvious malicious content, requires DCO sign-off, comments on failures, and attempts automatic approval and merge when checks pass.

Gatekeeper must only execute trusted scripts from the base branch and must not run contributor-branch code.

### Time Sentinel

Time Sentinel scans `community/` and can move Skills inactive for more than 180 days to `legacy/`.

### Chronicler

Chronicler archives legacy files into annual GitHub Releases and clears the legacy directory after successful publication.

### Resurrection Council

Anyone can start a resurrection vote with `/vote-resurrect {skill_name}`. If voting passes after 7 days with more than 50% support, the Skill can return to `community/`.

### AI and Agent Maintenance

The project encourages AI and agents to take on maintenance work. AI may perform mechanical checks, summaries, translations, duplicate-content hints, PR triage, lifecycle suggestions, public impact signal summaries, archive notes, and dispute summaries.

The goal is to free humans from repetitive maintenance so they can focus on whether their Skills are valuable, read, improved, and socially discussed.

AI judgments must be visible, reviewable, and overridable. AI must not have hidden privilege, bypass the charter to ban participants, privately change rules, or become a new authority.

If an agent's implementation is changed by the community and the system temporarily stalls, misjudges, or behaves differently, that too is part of the experiment. As long as legal, platform, security, and stability boundaries are not crossed, the fix should happen through public PRs, Issues, and rollback mechanisms rather than hidden human privilege.

AI maintenance failures should also be recorded as experimental data.

### Influence Sentinel

Influence Sentinel generates public impact signals:

- Sources must be auditable public objects: Git history, `community/*.md`, Issues, PRs, comments, Reactions, and resurrection votes.
- It outputs `community/index.json` for machines and `docs/impact.md` for humans.
- Scores are observation, ordering, and maintenance hints only. They must not directly ban a Skill, remove resurrection rights, or change equal authorship status.
- The formula must stay public. If a signal is abused, the project should publicly change the formula or weight instead of introducing hidden algorithms.

## 6. Revenue and Sponsorship

The project is not commercialization-driven.

But it is a social experiment. Its future is decided by public rules, community consensus, and later modifications. If it eventually creates revenue or evolves into a new rule model, that outcome is also part of the experiment.

The founder reserves no personal revenue right or distribution priority. The project may one day earn money while the founder receives nothing. If that follows public rules and community evolution, it is a valid experimental result.

The project does not actively seek sponsorship. If resources enter the project, they must be visible and governed by public rules.

## 7. Rule Changes

The charter, README, automation scripts, directory structure, lifecycle rules, and revenue rules can all be changed.

Changes should happen through public Issues or PRs. Changes to authorship, revenue, resurrection thresholds, archival periods, auto-merge scope, or participant rights should move slowly and visibly.

## 7.1 Capacity Boundaries and Pause Mechanism

The project acknowledges that the current technical path has capacity limits. The current stage uses a flat `community/` directory and simple scans. It is good enough to start the experiment, but it should not pretend to scale forever.

If user count or active Skill count suddenly reaches the critical threshold of the current design stage, the community may set `status: paused` in `governance/capacity.yml`. In paused status, Gatekeeper should reject new or updated active Skill PRs, while governance, documentation, translation, and architecture PRs may continue.

The pause is not punishment. It is a visible boundary control. It means the current architecture needs discussion before expansion continues.

Architecture adjustment remains community-maintained. Anyone can propose a registry, author sharding, multi-repository design, search index, or another approach. Once a proposal passes community voting or visible consensus, Skill PRs can resume.

If everyone gets stuck, that too is part of the experiment. Contribution may exist, or it may not. Many people are here simply to play, leave a name, and observe what the system becomes.

See `docs/capacity.md` and `governance/capacity.yml` for stages, thresholds, and resume conditions.

## 8. Conflict Between Charter and Scripts

## 8.1 Criticism and Service Continuity

Moral criticism, ordinary disagreement, misunderstanding, mockery, and public controversy are not service-stopping events by themselves. As long as the service is not broken by legal risk, platform-policy risk, malicious attack, or stability failure, being criticized can remain part of the experiment.

Copyright infringement, privacy exposure, harassment, hate, malware, credential theft, destructive abuse, platform-policy violations, and GitHub Actions permission abuse must be handled as priority risks.

See `docs/risks.md` for the risk model.

When the charter and current automation differ:

1. Current scripts represent what is already executable.
2. The charter represents the rule the community intends to align with.
3. If the mismatch affects governance, open an Issue or PR to fix either the script or the charter.

Rules are not stone tablets. They are navigation marks in the tide.

## 9. Final Line

Welcome to the experiment.

Try it, break it, fix it, and try again.
