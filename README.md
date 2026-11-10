# Mlarkanoid

An oldskool Arkanoid-style terminal game written in MLang. Neon brick rows,
Unicode block glyphs, momentum-driven paddle control, impact flashes, combo
scoring, three lives, and progressively faster waves with armored bricks.
Rendering uses `std::esc` from the sibling `../mlang` checkout.
An animated arcade welcome screen features a beveled metallic logo with a warm-to-cool gradient and sweeping glint, cycling neon
bricks, and a bouncing ball. Press **Space** or **Enter** to enter the game,
then **Space** to launch your first ball.

## Play

```sh
./run.sh
```

Requires an installed MLang compiler/runtime and the `../mlang/stdlib` sources.
Built and tested with **MLang 0.4.4.12**, from the 0.4.4 release series. The sibling
checkout's older `build/mlang` is not required. Use a UTF-8 ANSI terminal with
at least **64 columns × 24 rows** and a font supporting block/box glyphs.

| Key | Action |
| --- | --- |
| `h` / `←` | Accelerate left |
| `l` / `→` | Accelerate right |
| Space / Enter | Start from the welcome screen |
| Space | Launch the ball during play |
| `p` | Pause / resume |
| `r` | Restart, keeping the best score for this session |
| `q` / Ctrl-C | Quit |

Hold or repeat a direction to build paddle speed; reverse to brake and change
direction. Ball angle depends on where it hits the paddle and paddle momentum.
Standard terminals send key presses/repeats, but no key releases: movement
continues for 180 ms after the last repeat, then friction slows the paddle.
Your terminal/OS key-repeat delay affects the initial hold response.

Clear a wave for 500 bonus points. Consecutive brick breaks between paddle
hits multiply points up to ×8. `▓` bricks take two hits. Best score lasts until
the process exits. Shrinking the terminal suspends play until it fits again.

## Waves and colors

Eight layouts cycle with increasing ball speed and armor: Prism Wall, Neon
Windows, Fire Chevron, Ice Diamond, Checker Pop, Color Pillars, Fortress, and
Space Invader. Each has its own color arrangement: rainbow mosaics, alternating
neon colors, fiery patches, icy highlights, checker tiles, colored pillars,
fortress accents, and a green/cyan invader with magenta antennae.

## Falling capsules

Every third destroyed brick drops a colored letter capsule. Catch it with the
paddle for 100 points and its effect; missed capsules fall out of the arena.
The six capsule types cycle in order, including larger **[MLA]** and **[NUKE]** capsules.

| Capsule | Effect |
| --- | --- |
| **E** | Expand the paddle to 12 cells for 12 seconds |
| **S** | Slow the ball to 65% speed for 10 seconds |
| **C** | Catch the ball on the paddle for 12 seconds; Space releases it |
| **P** | Add one life, up to five |
| **MLA** | Cover the entire 60-cell arena with the paddle for 10 seconds |
| **NUKE** | Blast all remaining bricks and advance to the next wave |

Effects can coexist. Collecting the same capsule refreshes its timer. The status
bar shows remaining seconds; pause freezes capsules and timers. A lost life or
new wave clears capsules and temporary effects. When MLA expires, the paddle
returns to the center at its normal size (or expanded size if E is still active).

## Build and test

```sh
./scripts/build.sh          # builds build/mlarkanoid
./scripts/build.sh test     # deterministic physics tests via std::testing
python3 tests/terminal_smoke.py  # POSIX terminal/input/cleanup integration checks
```

The build prefers `~/.local/bin/mlang` when installed, then `mlang` on PATH.
Override toolchain locations if needed:

```sh
MLANG=/path/to/mlang MLANG_ROOT=/path/to/mlang-checkout ./run.sh
```

`MLANG_STDLIB_PATH` and `MLANG_STDLIB_LIB_PATH` can select alternate module and
native runtime directories. Keep the compiler, modules, and runtime compatible.
The runner restores the saved terminal settings and cursor on exit or signals.

## Source layout

- `src/game.mla`: deterministic fixed-point physics at 125 Hz and wave rules.
- `src/main.mla`: nonblocking keyboard input and buffered color rendering.
- `tests/game_tests.mla`: collisions, acceleration, lives, pause, and waves.
- `scripts/build.sh`: reproducible build/test entry point.

Use four-space indentation, `snake_case` functions/fields, and `PascalCase`
structs. Keep terminal I/O outside the physics module so behavior can be tested
without a terminal.
