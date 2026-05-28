# Issue tracker: GitHub

本仓库的 Issues 和 PRD 均存放在 GitHub Issues 中。所有操作通过 `gh` CLI 完成。

## 操作约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行正文使用 heredoc。
- **查看 issue**：`gh issue view <number> --comments`，可通过 `jq` 过滤评论并获取标签信息。
- **列出 issues**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，根据需要配合 `--label` 和 `--state` 过滤。
- **评论 issue**：`gh issue comment <number> --body "..."`
- **添加/移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭 issue**：`gh issue close <number> --comment "..."`

仓库信息通过 `git remote -v` 自动推断 — `gh` 在 clone 目录内运行时自动完成此操作。

## 当技能说"发布到 issue tracker"

创建一个 GitHub issue。

## 当技能说"获取相关工单"

执行 `gh issue view <number> --comments`。
