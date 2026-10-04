#!/usr/bin/env python3
"""解析井字棋逐行 JSON，不重新判断胜负。"""

import json
import subprocess
import unittest


_VALID_STATUS = {"in_progress", "x_wins", "o_wins", "draw"}


def parse_snapshot(line):
    """读取并校验一行版本化局面；胜负字段直接信任 C++ 协议。"""
    payload = json.loads(line)
    if payload.get("version") != 1:
        raise ValueError("不支持的协议版本")
    cells = payload["cells"]
    if len(cells) != 9 or any(cell not in {"X", "O", " "} for cell in cells):
        raise ValueError("cells 必须是九个 X、O 或空格")
    if payload["player"] not in {"X", "O"}:
        raise ValueError("player 必须是 X 或 O")
    if payload["status"] not in _VALID_STATUS:
        raise ValueError("未知对局状态")
    return {
        "version": 1,
        "sequence": payload["sequence"],
        "cells": list(cells),
        "player": payload["player"],
        "status": payload["status"],
        "winner": payload.get("winner", ""),
    }


def read_snapshots(lines):
    """按输入顺序解析快照，并拒绝重复或倒退的序号。"""
    snapshots = []
    previous = -1
    for line in lines:
        snapshot = parse_snapshot(line)
        if not isinstance(snapshot["sequence"], int) or snapshot["sequence"] <= previous:
            raise ValueError("sequence 必须严格递增")
        previous = snapshot["sequence"]
        snapshots.append(snapshot)
    return snapshots


def run_app(command, moves, timeout=8):
    """驱动阶段 app，分离 stdout/stderr，并限制协议进程等待时间。"""
    input_text = "\n".join(moves) + "\n"
    completed = subprocess.run(
        command, input=input_text, text=True, encoding="utf-8",
        capture_output=True, timeout=timeout, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "对局程序失败")
    snapshots = [line for line in completed.stdout.splitlines() if line.startswith("{")]
    return read_snapshots(snapshots)


def marks_from_cells(cells):
    """把九格转成坐标图用的 {(row, col): 文本}，空格略去。"""
    marks = {}
    for index, cell in enumerate(cells):
        if cell == " ":
            continue
        marks[(index // 3, index % 3)] = cell
    return marks


class SnapshotTest(unittest.TestCase):
    def test_parses_nine_cells_and_status(self):
        line = (
            '{"version":1,"sequence":1,"cells":["X","X","X","O","O",'
            '" "," "," "," "],"player":"X","status":"x_wins",'
            '"winner":"X"}'
        )
        snapshot = parse_snapshot(line)
        self.assertEqual(snapshot["status"], "x_wins")
        self.assertEqual(snapshot["winner"], "X")
        self.assertEqual(len(snapshot["cells"]), 9)
        self.assertEqual(marks_from_cells(snapshot["cells"])[(0, 2)], "X")

    def test_rejects_non_monotonic_sequence(self):
        line = '{"version":1,"sequence":0,"cells":[" "," "," "," "," "," "," "," "," "],"player":"X","status":"in_progress"}'
        self.assertEqual(read_snapshots([line])[0]["sequence"], 0)
        with self.assertRaises(ValueError):
            read_snapshots([line, line])


if __name__ == "__main__":
    unittest.main()
