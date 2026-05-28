# 为稷下观澜贡献

语言 / Languages: [English](CONTRIBUTING.md) | [简体中文](CONTRIBUTING.zh-CN.md)

欢迎。稷下观澜不是传统 Skill 商店，而是一场关于人机交互、人性、机器性与平权共生的开源社会实验。

## 贡献基本原则

- 每位参与者地位平等。
- 规则、争议和治理修改都应公开。
- 不要覆盖、冒名或恶意删除他人署名 Skill。
- 引用、改造、衍生他人 Skill 时保留原作者署名。
- 使用 Issue 或 PR 提出规则修改、表达异议、记录讨论。

## 提交 Skill

Skill 必须满足：

- 文件后缀为 `.md`。
- 位于 `community/` 目录。
- 包含 YAML Frontmatter。
- Frontmatter 至少包含 `title`、`author`、`tags`、`created_at`。
- `tags` 必须是 YAML 列表。
- 不包含破坏性命令、恶意载荷或隐藏行为。

示例：

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

每位参与者最多拥有 5 个活跃 Skill。Gatekeeper 会基于 `author` frontmatter 统计 `community/` 中的活跃 Skill 数量，并拒绝会让同一作者超过 5 个活跃 Skill 的 PR。

## 许可证

提交贡献即表示你同意贡献内容按本项目许可证发布：

- 代码、脚本、工作流：MIT License，见 `LICENSE`。
- 文档和 Skill 文本：CC BY-SA 4.0，见 `LICENSE-DOCS.md`。

## DCO 签署

所有 commit 必须包含 Developer Certificate of Origin 签署。

使用：

```bash
git commit -s -m "Add my skill"
```

这会添加：

```text
Signed-off-by: Your Name <your.email@example.com>
```

缺少 sign-off 的 Pull Request 会被 Gatekeeper 拒绝。

## 治理修改

修改 `CHARTER.md`、生命周期规则、复活门槛、作者权利或收益相关规则时，应优先公开讨论。

项目可以演化，规则也可以演化。重要的是演化过程必须可见。
