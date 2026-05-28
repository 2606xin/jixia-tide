# Risk Model

This project accepts criticism as part of the experiment. It does not accept preventable service collapse, legal exposure, platform-policy violations, or avoidable harm to participants.

## Core Posture

The Jixia Tide should remain:

- Open.
- Equal.
- Publicly governed.
- Legally cautious.
- Operationally stable.

Security and moderation should protect service continuity and participant experience without turning the project into a hidden hierarchy.

## Attacker Motivations

Profit is not the main attack incentive. More likely motives are:

1. **Narrative capture**
   Flood the project with low-quality or provocative Skills to change how the community feels.

2. **Proof-by-breakage**
   Exploit weak rules and then claim equal governance is impossible.

3. **Name farming**
   Abuse the `author` field, multiple accounts, or repeated submissions to occupy attention.

4. **Prompt or Skill poisoning**
   Hide harmful instructions, social-engineering language, or prompt injection inside a Skill.

5. **Maintenance exhaustion**
   Create excessive Issues, PRs, vote campaigns, translation disputes, or governance debates.

6. **Legal contamination**
   Submit copyrighted, private, defamatory, illegal, or policy-violating material so the project absorbs the risk.

7. **Actions or token abuse**
   Try to make automation execute untrusted contributor code or misuse workflow permissions.

## What Can Be Criticized Without Stopping Service

The project may be criticized for:

- Being naive.
- Being too simple.
- Being too idealistic.
- Having imperfect fairness.
- Using weak identity checks.
- Allowing public disagreement.
- Letting visible controversy happen.

These are not reasons to stop the service by themselves. They are observations within the experiment.

## What Must Be Treated as a Stop-and-Fix Risk

The project should act quickly when there is:

- Copyright or license infringement.
- Private personal information or doxxing.
- Harassment, hate, threats, or targeted abuse.
- Malware, credential theft, destructive instructions, or active abuse infrastructure.
- Attempts to execute untrusted code through GitHub Actions.
- Actions that threaten repository availability, token safety, or service continuity.
- Content that violates GitHub's Terms, Acceptable Use Policies, or Community Guidelines.

Relevant platform rules:

- GitHub Acceptable Use Policies: https://docs.github.com/site-policy/acceptable-use-policies/github-acceptable-use-policies
- GitHub Terms of Service: https://docs.github.com/en/site-policy/github-terms/github-terms-of-service/
- GitHub Community Guidelines: https://docs.github.com/articles/github-community-guidelines

## Stability Principles

1. **Do not pause for ordinary criticism**
   Criticism, mockery, or moral disagreement is not a service outage.

2. **Pause narrowly**
   If pausing is required, pause the smallest surface possible. For example, pause new Skill PRs but keep governance, translation, documentation, and architecture PRs open.

3. **Keep decisions public**
   Avoid private, unlogged governance where possible. Use Issues, PRs, labels, and commits.

4. **Prefer automation over discretion**
   Use clear gates for file paths, metadata, DCO sign-off, author quota, capacity status, and obvious malicious content.

5. **Do not trade equality for safety theater**
   Safety changes should not create permanent founder privilege, hidden allowlists, or arbitrary moderator power unless the community explicitly changes the rules.

6. **Legal and platform rules are hard boundaries**
   The experiment cannot require maintainers to host illegal, infringing, abusive, or platform-prohibited material.

## Current Defenses

- Gatekeeper only reads PR content through GitHub API and does not execute contributor branch code.
- PRs must only add or modify Markdown Skills under `community/`.
- Required frontmatter is checked.
- Obvious malicious command patterns are rejected.
- DCO sign-off is required.
- Each `author` is limited to 5 active Skills.
- Capacity can pause active Skill PRs through `governance/capacity.yml`.
- Authorship and attribution rules are written in `CHARTER.md`.
- Licensing and DCO are documented.

## Known Weaknesses

- `author` can be manipulated by changing spelling or identity.
- Reaction voting can be brigaded.
- Regex-based malicious content detection is shallow.
- Prompt injection can be subtle.
- Copyright violations may not be detectable automatically.
- Translations may drift from the Chinese source.
- GitHub repository ownership is not the same as perfect equality.

These weaknesses should be public. They are not excuses to give up; they are the next edges of the experiment.

## Legal Risk Handling

When legal risk appears:

1. Preserve public evidence where appropriate.
2. Remove or quarantine the risky content if required by law, license, or platform policy.
3. Open an Issue explaining the rule boundary without publishing private or harmful details.
4. Prefer narrow action over broad shutdown.
5. If money, contracts, tax, or legal entity questions arise, seek qualified legal advice before making binding commitments.

This document is not legal advice.

## Political and Cultural Language

The project can preserve its Chinese cultural origin without presenting itself as a political organization.

For global readability:

- Prefer cultural and experimental framing.
- Avoid unnecessary political labels in operational rules.
- Keep the core commitments: equality, public rules, founder non-privilege, and experiment-first governance.

## Final Principle

Being criticized is not failure.

Being forced offline by preventable legal, security, or stability failures is failure.

The system should stay open as long as it can do so lawfully, safely, and without abandoning equal participation.
