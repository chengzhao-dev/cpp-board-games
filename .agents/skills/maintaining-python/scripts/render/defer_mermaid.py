#!/usr/bin/env python3
"""渲染后为 mermaid 脚本标签添加 defer，避免阻塞首屏。

用法：python .agents/skills/maintaining-python/scripts/render/defer_mermaid.py [_book]
退出码：0。
"""

import re
import sys
from pathlib import Path

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_book")
if not out_dir.exists():
    out_dir = Path("_book")

_pattern = re.compile(r'(<script src="[^"]*mermaid[^"]*")>(?=</script>)')
changed = 0
for path in out_dir.rglob("*.html"):
    html = path.read_text(encoding="utf-8")
    new_html = _pattern.sub(r"\1 defer>", html)
    if new_html != html:
        path.write_text(new_html, encoding="utf-8")
        changed += 1

print(f"defer-mermaid: 已处理 {changed} 个 HTML 文件")
