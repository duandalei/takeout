# Domain Docs（领域文档）

工程类技能在探索代码库时应如何消费本仓库的领域文档。

## 探索前先阅读以下内容

- **`CONTEXT.md`**（仓库根目录），或
- **`CONTEXT-MAP.md`**（仓库根目录，如果存在）— 指向每个上下文的 `CONTEXT.md`。阅读与当前主题相关的每一个。
- **`docs/adr/`** — 阅读与你即将工作的领域相关的 ADR。多上下文仓库中，还需检查 `src/<context>/docs/adr/` 中上下文范围的决策。

如果以上任何文件不存在，**静默继续**。不要提示其缺失，不要主动建议创建。`/grill-with-docs` 技能会在术语或决策实际确定时按需创建。

## 文件结构

单上下文仓库（大多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md`）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 上下文相关的决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用术语表中的词汇

当你的输出涉及领域概念时（issue 标题、重构提案、假设、测试名称），请使用 `CONTEXT.md` 中定义的术语。不要偏离到术语表明确避免的同义词。

如果你需要的概念尚未出现在术语表中，这是一个信号 — 要么你在创造项目未使用的语言（需重新考虑），要么确实存在缺口（记录下以便 `/grill-with-docs` 处理）。

## 标记 ADR 冲突

如果你的输出与现有 ADR 矛盾，应显式指出而非静默覆盖：

> _与 ADR-0007（事件溯源订单）矛盾 — 但值得重新讨论，因为…_
