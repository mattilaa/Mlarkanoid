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
import tempfile


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
    score_directory = tempfile.TemporaryDirectory(prefix="mlarkanoid-terminal-")
    score_file = Path(score_directory.name) / "scores.tsv"
    score_file.write_text("ARCADE\t9999\t8\n")
    env["MLARKANOID_HIGHSCORE_FILE"] = str(score_file)
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
        paddles = [re.search(r"▐━+▌|━{8,}", line) for line in lines if line.startswith(" ║")]
        paddles = [match.start() for match in paddles if match]
        assert paddles, "Paddle was not rendered"
        return paddles[-1]

    try:
        intro = expect(b"PRESS SPACE OR ENTER")
        assert b"M L A R K A N O I D" in intro
        assert b"38;2;255;65;80" in intro, "Warm logo gradient was not rendered"
        assert b"38;2;65;85;210" in intro, "Cool logo gradient was not rendered"
        assert "▟".encode() in intro and "▓".encode() in intro, "Logo bevel/shadow missing"
        assert b"  SCORE " not in intro and b"READY" not in intro
        os.write(master, b"hlpr")
        idle = collect(0.15)
        assert b"38;2;255;65;80" not in idle, "Static logo was repainted during animation"
        assert b"38;2;65;85;210" not in idle, "Static gradient was repainted during animation"
        assert b"  SCORE " not in idle, "Gameplay keys bypassed the welcome screen"
        resize(18, 50)
        expect(b"Resize to at least")
        os.write(master, b" ")
        collect(0.05)
        resize(24, 80)
        resized = expect(b"PRESS SPACE OR ENTER")
        assert b"38;2;255;65;80" in resized, "Logo was not restored after resizing"
        if intro_only:
            os.write(master, quit_key)
            expect(b"\x1b[?1049l")
            process.wait(timeout=3)
            assert process.returncode == 0
            return
        os.write(master, b"t")
        hall = expect(b"HALL OF FAME")
        assert b"ARCADE" in hall and b"9999" in hall
        os.write(master, b"t")
        returned = expect(b"PRESS SPACE OR ENTER")
        assert b"38;2;255;65;80" in returned, "Logo was not restored after Hall of Fame"
        os.write(master, b"\r" if quit_key == b"q" else b" ")
        expect(b"ENTER YOUR PILOT NAME")
        os.write(master, b"tesx\x7ft\r")
        initial = expect(b"READY")
        assert b"9999" in initial
        plain_initial = ANSI.sub(b"", initial).decode(errors="replace")
        board_rows = [line for line in plain_initial.splitlines() if line.startswith(" ║")]
        paddle_rows = [line for line in board_rows if "━━━━━━" in line]
        assert paddle_rows
        if "--paddle-brackets" in command:
            assert "▐━━━━━━▌" in paddle_rows[-1]
        else:
            assert "━━━━━━━━" in paddle_rows[-1] and "▐" not in paddle_rows[-1] and "▌" not in paddle_rows[-1]
        assert b"PRISM WALL" in initial and b"CATCH:" in initial
        assert b"MLA full" in initial and b"NUKE" in initial
        assert b"D aim" in initial and b"H gap" in initial and b"F 2x" in initial and b"LSD" in initial and b"V up" in initial
        # The first brick row has several colors, rather than one row gradient.
        first_row = initial.split(b"\r\n")[6]
        assert len(set(re.findall(rb"\x1b\[(9[1-7])m", first_row))) >= 3
        assert "◆".encode() in first_row and "◇".encode() in first_row
        start_column = paddle_column(initial)
        moved = b""
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            os.write(master, b"l")
            moved += collect(0.05)
            if paddle_column(moved) >= start_column + 4:
                break
        assert paddle_column(moved) >= start_column + 4, "L did not move right"
        # An arrow escape sequence may arrive across multiple polling cycles.
        os.write(master, b"\x1b[")
        collect(0.01)
        os.write(master, b"D")
        moved_left = b""
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            moved_left += collect(0.05)
            os.write(master, b"\x1b[D")
            if paddle_column(moved_left) < paddle_column(moved) - 2:
                break
        assert paddle_column(moved_left) < paddle_column(moved) - 2, "Left arrow did not reverse"
        os.write(master, b" ")
        expect(b"COMBO")
        # The initial serve hits a brick within two seconds; its points autosave.
        deadline = time.monotonic() + 4
        while "TEST\t" not in score_file.read_text() and time.monotonic() < deadline:
            collect(0.05)
        assert "TEST\t" in score_file.read_text(), "Named score was not saved during play"
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
        # A completely new process must see the score earned above.
        process = subprocess.Popen(
            [str(ROOT / "build/mlarkanoid")], cwd=ROOT,
            stdin=slave, stdout=slave, stderr=slave, env=env
        )
        expect(b"PRESS SPACE OR ENTER")
        os.write(master, b"t")
        reloaded = expect(b"HALL OF FAME")
        assert b"TEST" in reloaded and b"ARCADE" in reloaded, "Scores did not survive restart"
        os.write(master, b"q")
        expect(b"\x1b[?1049l")
        process.wait(timeout=3)
        assert process.returncode == 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        os.close(master)
        os.close(slave)
        score_directory.cleanup()


if __name__ == "__main__":
    binary = str(ROOT / "build/mlarkanoid")
    help_result = subprocess.run([binary, "--help"], capture_output=True, text=True)
    assert help_result.returncode == 0 and "--paddle-brackets" in help_result.stdout
    assert "--lsd-rate" in help_result.stdout
    for value in ["-1", "101", "no", "1.5", "", "1000"]:
        rate_result = subprocess.run([binary, "--lsd-rate", value], capture_output=True, text=True)
        assert rate_result.returncode == 2 and "percentage" in rate_result.stdout
    missing_rate = subprocess.run([binary, "--lsd-rate"], capture_output=True, text=True)
    assert missing_rate.returncode == 2
    for value in ["0", "25", "100"]:
        rate_help = subprocess.run([binary, "--lsd-rate", value, "--help"], capture_output=True, text=True)
        assert rate_help.returncode == 0
    invalid_result = subprocess.run([binary, "--invalid-option"], capture_output=True, text=True)
    assert invalid_result.returncode == 2 and "Unknown option" in invalid_result.stdout
    check_session([str(ROOT / "build/mlarkanoid")], b"q")
    check_session([str(ROOT / "run.sh"), "--paddle-brackets", "--lsd-rate", "25"], b"\x03")
    check_session([str(ROOT / "build/mlarkanoid")], b"q", intro_only=True)
    print("PASS: welcome, name entry/editing, Hall of Fame, persistent scores across restart, detailed bricks, gameplay, cleanup")
