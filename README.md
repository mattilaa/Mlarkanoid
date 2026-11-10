# Mlarkanoid

An oldskool Arkanoid-style terminal game written in MLang. Neon brick rows,
Unicode block glyphs, momentum-driven paddle control, impact flashes, combo
scoring, three lives, and progressively faster waves with armored bricks.
Rendering uses `std::esc` from the sibling `../mlang` checkout.
An animated arcade welcome screen features a beveled metallic logo with a warm-to-cool gradient and sweeping glint, cycling neon
bricks, and a bouncing ball. Press **Space** or **Enter**, type your pilot
name, then press **Enter** to play. **Space** launches your first ball.

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
| `r` | Restart with the same pilot |
| `t` | Open / close the Hall of Fame; gameplay freezes while viewing |
| `n` | Enter a new pilot name after game over |
| `q` / Ctrl-C | Quit |

Hold or repeat a direction to build paddle speed; reverse to brake and change
direction. Ball angle depends on where it hits the paddle and paddle momentum.
Standard terminals send key presses/repeats, but no key releases: movement
continues for 180 ms after the last repeat, then friction slows the paddle.
Your terminal/OS key-repeat delay affects the initial hold response.

Clear a wave for 500 bonus points. Consecutive brick breaks between paddle
hits multiply points up to ×8. Armored bricks take two or three hits; their
plates crack as they weaken. Shrinking the terminal suspends play until it fits again.

## Persistent high scores

The Hall of Fame keeps the **top 10 different pilots**, with one personal best
per name. Names are up to 12 characters (`A-Z`, `0-9`, `_`, `-`); lowercase is
converted to uppercase and spaces become underscores. Backspace edits the name;
an empty name uses `PLAYER`. Equal scores rank by the highest wave reached.

Scores save automatically as points improve, including before game over, and
survive quitting, restarting a game, or restarting the application. Press **T**
on the welcome screen or during play to view the table. It opens automatically
at game over. **R** retries with the same pilot; **N** enters another name.

The default file is `~/.local/share/mlarkanoid/highscores.tsv` (or
`$XDG_DATA_HOME/mlarkanoid/highscores.tsv` when configured). To choose another:

```sh
MLARKANOID_HIGHSCORE_FILE=/path/to/highscores.tsv ./run.sh
```

The game creates the directory and replaces the file atomically. Invalid rows
are ignored when loading. If saving fails, the table marks the failure and the
game retries on exit. Scores are local to this computer.

## Waves and colors

Eight layouts cycle with increasing ball speed and armor: Prism Wall, Neon
Windows, Fire Chevron, Ice Diamond, Checker Pop, Color Pillars, Fortress, and
Space Invader. Each has its own color arrangement: rainbow mosaics, alternating
neon colors, fiery patches, icy highlights, checker tiles, colored pillars,
fortress accents, and a green/cyan invader with magenta antennae. Each brick
has four detailed glyph cells: diamond cores (`▐◆◇▌`), rails (`╞══╡`),
sloped lava tiles (`◢▓▒◣`), crystal facets, checker caps, lattice pillars,
fortress studs, or alien eyes. Armored caps (`╔▓▓╗`, `╔╬╬╗`) change to
cracked plates (`╭░╱╮`) after damage.

## Falling capsules

Every third destroyed brick drops a colored letter capsule. Catch it with the
paddle for 100 points and its effect; missed capsules fall out of the arena.
The six capsule types cycle in order, including larger **MLA** and **NUKE** capsules.
They appear as solid dark colored tiles with white letters and padded edges,
without brackets: blue E, amber S, green C, purple P, teal MLA, and red NUKE.

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
- `src/main.mla`: nonblocking input, name entry, Hall of Fame, and rendering.
- `src/highscores.mla`: top-10 ranking, validated loading, and atomic saving.
- `src/bricks.mla`: themed brick glyphs and visible armor damage.
- `tests/game_tests.mla`: collisions, acceleration, lives, pause, and waves.
- `tests/highscore_tests.mla`: ranking, persistence, file errors, and brick glyphs.
- `scripts/build.sh`: reproducible build/test entry point.

Use four-space indentation, `snake_case` functions/fields, and `PascalCase`
structs. Keep terminal I/O outside the physics module so behavior can be tested
without a terminal.
