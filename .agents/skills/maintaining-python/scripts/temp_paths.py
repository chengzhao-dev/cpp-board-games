"""仓库级临时产物路径。

所有需要可回收的项目中间文件都写入根目录 ``temp/<purpose>``。系统临时目录
只保留给不属于本项目的第三方进程。
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMP_ROOT = ROOT / "temp"


def temp_dir(purpose: str) -> Path:
    """返回并创建一个用途明确的仓库临时目录。"""
    if not purpose or "/" in purpose or "\\" in purpose or purpose in {".", ".."}:
        raise ValueError("purpose must be one directory name")
    path = TEMP_ROOT / purpose
    path.mkdir(parents=True, exist_ok=True)
    return path
