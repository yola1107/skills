# Kratos Skills — v3

A locally maintained Kratos v3 reference skill, adapted from [lwx-cloud/kratos-skills](https://github.com/lwx-cloud/kratos-skills). The upstream package declares MIT licensing; see its [license](https://github.com/lwx-cloud/kratos-skills/blob/main/LICENSE).

Start with [SKILL.md](SKILL.md). It routes to 23 topic guides plus a shared [version baseline](references/version-baseline.md); load only the topic needed for the task. Existing repository architecture, dependency pins and execution permissions take precedence.

This edition uses v3 core APIs, slog and independent v3 contrib modules. It replaces unsupported examples and absolute architecture rules with version-aware guidance. Database libraries, code generators, registries and telemetry remain project choices.

## Use

Invoke `$kratos-skills` with a concrete Kratos task. Keep this folder in the skill directory supported by your agent. [Usage notes](getting-started/claude-code-guide.md) explain the workflow; [中文说明](README_CN.md) describes the same package.

See [local update guidance](getting-started/claude-code-guide.md#更新本地修订) for recovery and upstream comparisons. Framework usage follows the [official documentation](https://go-kratos.dev/zh-cn/docs/); project contracts and pinned module source remain authoritative for the task. Documentation is not integration-test evidence.
