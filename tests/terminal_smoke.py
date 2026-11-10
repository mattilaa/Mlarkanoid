"""Exercise the actual terminal loop on POSIX, using only Python's stdlib."""

import fcntl
import os
from pathlib import Path
import pty
import re
import select
import struct
import subprocess
import termios
import time


ROOT = Path(__file__).resolve().parents[1]
ANSI = re.compile(rb"\x1b\[[0-9;?]*[A-Za-z]")


def check_session(command, quit_key, intro_only=False):
    master, slave = pty.openpty()

    def resize(rows, cols):
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))

    resize(24, 80)
    saved = termios.tcgetattr(slave)
    env = dict(os.environ, TERM="xterm-256color", MLANG_FORCE_ANSI="1")
    env.pop("NO_COLOR", None)
    process = subprocess.Popen(
        command, cwd=ROOT, stdin=slave, stdout=slave, stderr=slave, env=env
    )

    def collect(duration):
        output = b""
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            if select.select([master], [], [], max(0, deadline - time.monotonic()))[0]:
                output += os.read(master, 65536)
        return output

    def expect(token):
        output = b""
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            output += collect(0.05)
            if token in output:
                return output
            assert process.poll() is None, output.decode(errors="replace")
        raise AssertionError(f"Timed out waiting for {token!r}")

    def paddle_column(output):
        lines = ANSI.sub(b"", output).decode(errors="replace").splitlines()
        paddles = [line.index("▐") for line in lines if "▐" in line]
        assert paddles, "Paddle was not rendered"
        return paddles[-1]

    try:
        intro = expect(b"PRESS SPACE OR ENTER")
        assert b"M L A R K A N O I D" in intro
        assert b"38;2;255;65;80" in intro, "Warm logo gradient was not rendered"
        assert b"38;2;65;85;210" in intro, "Cool logo gradient was not rendered"
        assert "▟".encode() in intro and "▓".encode() in intro, "Logo bevel/shadow missing"
        assert b"SCORE" not in intro and b"READY" not in intro
        os.write(master, b"hlpr")
        idle = collect(0.1)
        assert b"SCORE" not in idle, "Gameplay keys bypassed the welcome screen"
        resize(18, 50)
        expect(b"Resize to at least")
        os.write(master, b" ")
        collect(0.05)
        resize(24, 80)
        expect(b"PRESS SPACE OR ENTER")
        if intro_only:
            os.write(master, quit_key)
            expect(b"\x1b[?1049l")
            process.wait(timeout=3)
            assert process.returncode == 0
            return
        os.write(master, b"\r" if quit_key == b"q" else b" ")
        initial = expect(b"READY")
        start_column = paddle_column(initial)
        moved = b""
        for _ in range(8):
            os.write(master, b"l")
            moved += collect(0.05)
        assert paddle_column(moved) > start_column, "L did not move right"
        # An arrow escape sequence may arrive across multiple polling cycles.
        os.write(master, b"\x1b[")
        collect(0.01)
        os.write(master, b"D")
        moved_left = b""
        for _ in range(24):
            moved_left += collect(0.05)
            os.write(master, b"\x1b[D")
        assert paddle_column(moved_left) < paddle_column(moved), "Left arrow did not reverse"
        os.write(master, b" ")
        expect(b"COMBO")
        os.write(master, b"p")
        paused = expect(b"PAUSED")
        later = collect(0.08)
        # Each full frame is the same while paused.
        def board(output):
            text = ANSI.sub(b"", output).decode(errors="replace")
            return re.findall(r" ╔.*? ╚[^\r\n]*", text, re.S)[-1]
        assert board(paused) == board(later), "Paused board changed"
        os.write(master, b"r")
        expect(b"READY")
        resize(18, 50)
        expect(b"Resize to at least")
        resize(24, 80)
        expect(b"READY")
        collect(0.04)
        os.write(master, quit_key)
        tail = expect(b"\x1b[?1049l")
        process.wait(timeout=3)
        tail += collect(0.05)
        assert process.returncode == 0
        restored = termios.tcgetattr(slave)
        # macOS may set PENDIN while switching queued input back to cooked mode.
        transient = getattr(termios, "PENDIN", 0)
        saved[3] &= ~transient
        restored[3] &= ~transient
        assert restored == saved, f"Terminal attributes were not restored: {saved!r} -> {restored!r}"
        assert b"\x1b[?25h" in tail and b"\x1b[?1049l" in tail
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        os.close(master)
        os.close(slave)


if __name__ == "__main__":
    check_session([str(ROOT / "build/mlarkanoid")], b"q")
    check_session([str(ROOT / "run.sh")], b"\x03")
    check_session([str(ROOT / "build/mlarkanoid")], b"q", intro_only=True)
    print("PASS: welcome, Space/Enter start, intro quit/resize, gameplay, Q/Ctrl-C, cleanup")
