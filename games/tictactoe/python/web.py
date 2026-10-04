#!/usr/bin/env python3
"""本地网页：先选双人或人机，人机再选难度，然后在棋盘上落子。

规则仍由 03-line-protocol 的 app 计算。本文件只打开页面，并把点击写成
该程序已经在读的两行选择和「行 列」。
"""

import json
import os
import queue
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_EOF = object()
HOST = "127.0.0.1"
PORT = 8765
MAX_BODY = 4096

# 页面只服务这一局。重新选择对局时关掉上一局进程。
SESSION = None
SESSION_LOCK = threading.Lock()


def opening_lines(mode, strength):
    """网页上的选择对应终端里的两行数字。双人只有第一行。"""
    if mode == "two":
        return ["1"]
    levels = {"random": "1", "heuristic": "2", "minimax": "3"}
    if strength not in levels:
        raise ValueError("未知难度")
    return ["2", levels[strength]]


def app_command():
    """拼出 app 的启动命令。Windows 上交给 WSL，因为二进制是 Linux 程序。"""
    binary = STAGE / "build" / "bin" / "app"
    if not binary.is_file():
        raise FileNotFoundError(binary)
    if os.name == "nt":
        text = STAGE.as_posix()
        root = "/mnt/" + text[0].lower() + text[2:]
        script = (
            f"cd '{root}' && exec env LD_LIBRARY_PATH=build/lib ./build/bin/app"
        )
        return ["wsl.exe", "bash", "-lc", script], None
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(STAGE / "build" / "lib")
    return [str(binary)], env


class MatchSession:
    """握住一个 app 进程，把终端提示和 JSON 行收进队列。"""

    def __init__(self):
        command, env = app_command()
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
        )
        self.lines = queue.Queue()
        self.errors = []
        self._start_pumps()

    def _start_pumps(self):
        """stdout 按行进队列；stderr 另存，避免管道写满把对局卡住。"""
        threading.Thread(target=self._pump_out, daemon=True).start()
        threading.Thread(target=self._pump_err, daemon=True).start()

    def _pump_out(self):
        for line in self.proc.stdout:
            self.lines.put(line.rstrip("\r\n"))
        self.lines.put(_EOF)

    def _pump_err(self):
        for line in self.proc.stderr:
            text = line.rstrip("\r\n")
            if text:
                self.errors.append(text)

    def _write(self, line):
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def _next_line(self, timeout):
        try:
            return self.lines.get(timeout=timeout)
        except queue.Empty:
            return None

    def _wait_for(self, marker, timeout=8):
        """读到含 marker 的一行，或进程结束。返回期间最后一条 JSON。"""
        latest = None
        waited = 0.0
        while waited < timeout:
            line = self._next_line(0.2)
            waited += 0.2
            if line is _EOF or (line is None and self.proc.poll() is not None):
                break
            if line is None:
                continue
            if line.startswith("{"):
                latest = json.loads(line)
            if marker in line:
                return latest
        if latest is None:
            raise TimeoutError(marker)
        return latest

    def begin(self, mode, strength):
        """先等到对局选择，再送难度，最后返回开局的九格。"""
        self._wait_for("请选择对局")
        lines = opening_lines(mode, strength)
        self._write(lines[0])
        if len(lines) == 2:
            self._wait_for("请选择难度")
            self._write(lines[1])
        return self._wait_for("请输入行和列")

    def move(self, row, col):
        """送一步人类落子。人机时后手会在同一次等待里下完。"""
        self._write(f"{row} {col}")
        latest = None
        waited = 0.0
        while waited < 8:
            line = self._next_line(0.2)
            waited += 0.2
            if line is _EOF or (line is None and self.proc.poll() is not None):
                break
            if line is None:
                continue
            if line.startswith("{"):
                latest = json.loads(line)
            if "请输入行和列" in line:
                break
        if latest is None:
            raise TimeoutError("局面")
        latest["message"] = self.errors[-1] if self.errors else ""
        self.errors.clear()
        return latest

    def close(self):
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait(timeout=3)


PAGE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>井字棋</title>
<style>
  :root { color-scheme: light dark; --fg: #1F2328; --bg: #ffffff; --line: #d0d7de; --raised: #f6f8fa; }
  @media (prefers-color-scheme: dark) {
    :root { --fg: #CDD9E5; --bg: #22272E; --line: #444c56; --raised: #2d333b; }
  }
  body { margin: 0; color: var(--fg); background: var(--bg);
    font-family: "LXGW WenKai Screen", "Noto Sans CJK SC", "Segoe UI", sans-serif; }
  main { max-width: 24rem; margin: 2rem auto; padding: 0 1rem; }
  h1 { font-size: 1.5rem; font-weight: 400; }
  button { font: inherit; color: var(--fg); background: var(--raised);
    border: 1px solid var(--line); border-radius: 0.4rem; padding: 0.6rem 1rem; }
  .choices { display: flex; gap: 0.75rem; flex-wrap: wrap; }
  .board { display: grid; grid-template-columns: repeat(3, 4.5rem); gap: 0.4rem; }
  .board button { height: 4.5rem; font-size: 1.75rem; }
  .hidden { display: none; }
  p { line-height: 1.7; }
</style>
</head>
<body>
<main>
  <h1>井字棋</h1>
  <section id="mode">
    <p>先选择对局。</p>
    <div class="choices">
      <button type="button" id="two">双人</button>
      <button type="button" id="cpu">人机</button>
    </div>
  </section>
  <section id="level" class="hidden">
    <p>再选择难度。</p>
    <div class="choices">
      <button type="button" data-strength="random">随机</button>
      <button type="button" data-strength="heuristic">启发式</button>
      <button type="button" data-strength="minimax">极小极大</button>
    </div>
  </section>
  <section id="play" class="hidden">
    <p id="status"></p>
    <div class="board" id="board"></div>
  </section>
</main>
<script>
const modeBox = document.getElementById("mode");
const levelBox = document.getElementById("level");
const playBox = document.getElementById("play");
const board = document.getElementById("board");
const status = document.getElementById("status");
const names = {in_progress: "进行中", x_wins: "X 获胜", o_wins: "O 获胜", draw: "平局"};

function showBoard(snapshot) {
  modeBox.classList.add("hidden");
  levelBox.classList.add("hidden");
  playBox.classList.remove("hidden");
  status.textContent = names[snapshot.status] || snapshot.status;
  board.replaceChildren();
  snapshot.cells.forEach((cell, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = cell === " " ? "" : cell;
    const done = snapshot.status !== "in_progress" || cell !== " ";
    button.disabled = done;
    button.addEventListener("click", () => sendMove(index));
    board.appendChild(button);
  });
}

async function post(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

async function begin(mode, strength) {
  showBoard(await post("/api/session", {mode, strength}));
}

async function sendMove(index) {
  showBoard(await post("/api/move", {row: Math.floor(index / 3), col: index % 3}));
}

document.getElementById("two").addEventListener("click", () => begin("two", null));
document.getElementById("cpu").addEventListener("click", () => {
  modeBox.classList.add("hidden");
  levelBox.classList.remove("hidden");
});
levelBox.querySelectorAll("button").forEach((button) => {
  button.addEventListener("click", () => begin("cpu", button.dataset.strength));
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "-1"))
            if length < 0 or length > MAX_BODY:
                raise ValueError("请求体过大或缺少长度")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = self._dispatch(payload)
        except (TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
            message = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
            status = 400 if isinstance(error, (ValueError, json.JSONDecodeError)) else 500
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)
            return
        body = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _dispatch(self, payload):
        global SESSION
        if not isinstance(payload, dict):
            raise ValueError("JSON 请求必须是对象")
        with SESSION_LOCK:
            if self.path == "/api/session":
                mode = payload.get("mode")
                strength = payload.get("strength")
                if mode not in {"two", "cpu"}:
                    raise ValueError("未知对局模式")
                if mode == "cpu" and strength not in {"random", "heuristic", "minimax"}:
                    raise ValueError("未知难度")
                if SESSION is not None:
                    SESSION.close()
                SESSION = MatchSession()
                snapshot = SESSION.begin(mode, strength)
                snapshot["message"] = ""
                return snapshot
            if self.path == "/api/move":
                if SESSION is None:
                    raise ValueError("还没有选择对局")
                row = payload.get("row")
                col = payload.get("col")
                if not isinstance(row, int) or not isinstance(col, int):
                    raise ValueError("坐标必须是整数")
                if not (0 <= row < 3 and 0 <= col < 3):
                    raise ValueError("坐标超出棋盘")
                return SESSION.move(row, col)
        raise ValueError("未知路径")

    def log_message(self, fmt, *args):
        return


def serve():
    """只监听本机。打开浏览器后按页面上的顺序选择。"""
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"http://{HOST}:{PORT}")
    server.serve_forever()


class WebFlowTest(unittest.TestCase):
    def test_opening_lines_match_terminal_menu(self):
        self.assertEqual(opening_lines("two", None), ["1"])
        self.assertEqual(opening_lines("cpu", "minimax"), ["2", "3"])

    def test_page_asks_mode_before_strength(self):
        self.assertIn("先选择对局", PAGE)
        self.assertIn("再选择难度", PAGE)
        self.assertLess(PAGE.index("双人"), PAGE.index("极小极大"))


if __name__ == "__main__":
    serve()
