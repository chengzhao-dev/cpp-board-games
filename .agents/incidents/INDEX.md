# 事故索引

排查失败时才读本文件；平时把 `.agents/incidents/` 视为不存在。命中关键词后打开对应案例，按「症状 → 根因 → 修复方案」对照排查。

| 关键词 | 案例 |
| --- | --- |
| GitHub Desktop、Publish repository、push 失败、远端 404、connection reset、curloptResolve | github/desktop-publish-and-push-failure.md |
| GitHub Pages、404、乱码、site-url、Pages source、gh-pages、发布前检查 | github/pages-mojibake-and-source-drift.md |

## 新增案例

案例文件放 `<domain>/<topic>.md`，正文顺序：frontmatter → `# 标题` → 日期与关键词 → `## 症状` → `## 根因` → `## 修复方案` →（可选）`## 验证方法`。写入后必须回到本表登记关键词。
