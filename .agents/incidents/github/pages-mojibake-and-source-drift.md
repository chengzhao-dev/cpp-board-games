---
domain: github
date: 2026-09-29
---

# GitHub Pages 站点 404 与乱码：渲染全绿但线上打不开

**日期**：2026-09-29　**关键词**：GitHub Pages、404、乱码、site-url、Pages source、gh-pages、发布前检查

## 症状

- `https://chengzhao-dev.github.io/cpp-board-games/` 打不开：HTTP 404（Site not found），或打开后中文乱码。
- Actions 里 `quarto build & deploy` 全绿，没有任何一步报错。

## 根因

1. Pages 源从未配置成功：`GET /repos/:repo/pages` 返回 404。workflow 里纠正 Pages 源的 curl 步骤把非预期返回**降级成 warning**，job 照样绿，问题被掩盖。
2. `_quarto.yml` 缺少 `book.site-url`，Quarto 不生成 `sitemap.xml`，站内相对链接在子路径部署下可能失效。
3. `content/` 与 `games/` 的编码检查默认是软报告（soft），乱码文件不阻断 CI，直接渲染发布。
4. 发布 workflow 只跑 `quarto render`，没有跑仓库统一校验入口，也没有对 `_book/` 做发布前 smoke 检查。

## 修复方案

1. `_quarto.yml` 的 `book:` 下补 `site-url: "https://chengzhao-dev.github.io/cpp-board-games"`（与 `repo-url` 同级）。
2. 发布 workflow（`pages.yml`）按顺序执行：渲染前 `run.py check --profile fast` → `quarto render` → `defer_mermaid.py` → 渲染后 `run.py check --profile full`（含发布产物 smoke 检查 `check_book_output.py`）→ 发布 `gh-pages`。
3. Pages 源纠正步骤（`POST`/`PUT /repos/:repo/pages`）遇到非 `200/201/202/409` 返回时 `exit 1`，不允许降级成 warning。
4. 仓库统一校验入口即 `run.py check`；`check_book_output.py` 检查 `_book/index.html` 存在、charset、BOM/U+FFFD/乱码特征、`sitemap.xml` 就绪（Book 项目的 site-url 生效标志）。

## 验证方法

- `curl -s -o /dev/null -w "%{http_code}" https://chengzhao-dev.github.io/cpp-board-games/` 返回 200。
- `GET /repos/chengzhao-dev/cpp-board-games/pages` 返回 200，且 `source` 为 `gh-pages` `/`。
- 本地发布前预演：`run.py render` 后 `run.py check --profile book` 全绿（`book-output` 项即 smoke 检查）。
