# Issue 追踪器：GitHub

本仓库的 issues 和 PRD 存放在 GitHub Issues 中。所有操作使用 `gh` CLI。

## 操作约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行正文使用 heredoc。
- **读取 issue**：`gh issue view <number> --comments`，用 `jq` 过滤评论，同时获取标签。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，配合 `--label` 和 `--state` 过滤。
- **评论 issue**：`gh issue comment <number> --body "..."`
- **添加 / 移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭 issue**：`gh issue close <number> --comment "..."`

仓库名通过 `git remote -v` 推断 —— `gh` 在 clone 下来的仓库中自动完成这一步。

## 当 skill 说"发布到 issue 追踪器"时

创建一个 GitHub issue。

## 当 skill 说"获取相关工单"时

执行 `gh issue view <number> --comments`。
