# QA evidence and scope

`reports/` contains selected recorded results from the full private v0.4.17 and pre-RC checkpoints. `evidence/` contains representative before/after and smoke-test contact sheets. The full private checkpoint retains raw screenshots, WRAM dumps and the environmental gallery referenced by historical reports; not every old evidence path is included in this public repository.

Current runnable scripts are under `scripts/` and use OUTDIR supplied by `tools/run_mesen.py`. Results go to `qa/generated/`, which is excluded from Git. The runner requires an existing Linux Mesen executable; it creates portable settings beside that executable if missing. It does not download models, BIOS files or an emulator.

| Script | Access | Scope |
|---|---|---|
| `options_sweep.lua` | Buttons | 15 option combinations/captures, 3,000 frames |
| `pause_resume.lua` | Buttons | Pause, resume, END RUN, 6,200 frames |
| `continue_game.lua` | Buttons | Kanku loss and CONTINUE; use `--index 5 --frames 14500` |
| `selector_natural.lua` | Buttons | Both pages and six course selections, 2,100 frames |
| `natural_course.lua` | Buttons by default | Verifies requested selector index at frame 1,450 |
| `gameover_trace.lua` | Buttons by default | Kanku RUN ABORTED; use `--index 5 --frames 13200` |
| `ended_consumer_assisted.lua` | WRAM substate injection | Actual RUN ENDED consumer, 1,100 frames; not natural completion |

The optional `--freeze` is assisted access and must remain labelled as such. Scripts have different internal stopping rules; pass the documented frame budget where indicated. The runner imposes 85/90-second limits.

Historical reports support only their documented scope. Five recent ledger entries are not a global text denominator. Graphics counts are not translation counts. This project remains TEST until the applicable gates in `docs/TRANSLATION_RULES.md` are supported by evidence.
