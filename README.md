# CG:SHOP 2027; multi-robot lawn mowing

SIGma's group submission for the [CG:SHOP 2027](https://cgshop.ibr.cs.tu-bs.de/competition/cg-shop-2027/) challenge.

## Fork and clone

1. Open [SIGma-UIUC/CG-SHOP-27](https://github.com/SIGma-UIUC/CG-SHOP-27) on GitHub.
2. Click **Fork** to create a copy under your account.
3. Install [Git](https://git-scm.com/downloads), then clone your fork. Replace
   `YOUR-USERNAME` with your GitHub username:

```sh
git clone https://github.com/YOUR-USERNAME/CG-SHOP-27.git
cd CG-SHOP-27
git remote add upstream https://github.com/SIGma-UIUC/CG-SHOP-27.git
```

`origin` points to your fork; `upstream` points to the team's repository.

## Set up the environment

Install a current version of
[uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the
cloned repository's root:

```sh
cd src/utils
uv python install 3.14.0
uv sync --python 3.14.0
```

These commands create `.venv` with Python 3.14.0 and install the dependencies.

Activate the environment using the command for your terminal:

| Terminal | Activation command |
| --- | --- |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| macOS/Linux bash or zsh | `source .venv/bin/activate` |

Keep your terminal in `src/utils` with the environment activated for all
commands below. Activate it again whenever you open a new terminal.
You can check the selected Python version with `python --version`.

After dependency changes, run `uv sync --python 3.14.0` again.
Run `deactivate` when you are finished to leave the environment.

## Verify an example solution

From `src/utils`, run this as one line:

```sh
python verify.py ../examples/test_instances1/srpg_246_821_1s3.instance.json ../examples/test_solutions1/srpg_246_821_1s3.solution.json
```

A feasible solution prints:

```text
=== got 0 errors ===
```

This checks an existing solution against its instance; it does not generate
routes. Replace both filenames with a matching instance/solution pair to check
another example or your own solver's output.

## Display a solution

From `src/utils`, run this as one line:

```sh
python display.py ../examples/test_instances1/srpg_246_821_1s3.instance.json ../examples/test_solutions1/srpg_246_821_1s3.solution.json
```

This opens a plot showing the cutter routes and swept area, with uncovered
cells in red. It also prints the longest route's length. Close the plot window
to return to your terminal. Use a matching instance/solution pair for other
examples or your own solver's output.

To save the plot instead of opening a window (also works without a graphical
display), add `--output`:

```sh
python display.py ../examples/test_instances1/srpg_246_821_1s3.instance.json ../examples/test_solutions1/srpg_246_821_1s3.solution.json --output ../examples/solution.png
```

Open the PNG in VS Code or an image viewer.

## Animate a solution

With the environment activated, run from `src/utils`:

```sh
python display.py ../examples/test_instances1/srpg_246_821_1s3.instance.json ../examples/test_solutions1/srpg_246_821_1s3.solution.json --animate
```

The window shows the cutters moving along their routes and the swept area
growing behind them. Close the window to return to your terminal.

To save a GIF instead of opening a window:

```sh
python display.py ../examples/test_instances1/srpg_246_821_1s3.instance.json ../examples/test_solutions1/srpg_246_821_1s3.solution.json --animate --output ../examples/solution.gif
```

GIF export can take a while. Animated output must have a `.gif` extension;
without `--animate`, the script still produces a static plot.

## Benchmark solvers

Each solver lives under `src/solver/<name>/` and supplies a `pyproject.toml`,
locked dependencies, and this directory-based command interface:

```sh
uv run --no-sync --project src/solver/<name> python src/solver/<name>/main.py OUTPUT --instances INPUT_DIRECTORY
```

The evaluator gives it one instance at a time and expects exactly one
`*.solution.json` file. Install dependencies before benchmarking so downloads
are excluded from the timings:

```sh
uv sync --frozen --project src/utils
uv sync --frozen --project src/solver/py-bounding-rect-solver
uv run --no-sync --project src/utils python src/utils/eval-solver.py src/examples/test_instances1 --solver-root proposed=src/solver --sample 15 --timeout 30 --animate
```

Run these commands from the repository root. Open `benchmark-results/report.md`
for the per-instance table. Generated reports, logs, solutions, and animations
are not committed.

- The default solver benchmark uses 15 fixed instances spanning multiple field
  sizes and families. `BENCHMARK_INSTANCES` names the exact files, and
  `sample.json` records their UIDs and input hashes.
- Coverage efficiency is **field area / total swept area**. Only validated
  solutions are scored, and the numerator excludes field holes. The total is
  the sum of every cutter footprint swept along every tour edge, including
  coverage outside the field. Overlap and revisits count every time they occur,
  so repeating a tour makes the score smaller. Valid solutions score between
  0 and 1, including stationary cutters. Maximum route length remains the
  optimization objective and ranking metric.
- Time and memory are measured by BenchExec for the complete solver process
  tree, including interpreter/uv startup and output writing. The benchmark
  workflow runs on Linux because BenchExec relies on Linux cgroups for reliable
  process-tree resource accounting. Validation and GIF generation have separate
  timeouts and are excluded from both measurements.
- Local non-Linux runs retain wall-time enforcement, but show memory as
  unavailable rather than publishing a less reliable process-tree estimate.
- Invalid, missing, crashed, and timed-out solutions remain in the report and
  make the evaluator exit nonzero. Animation failure does not invalidate a solver.
- The leaderboard ranks valid count first, then the mean of best valid length /
  solver length across the same sample. Failed cases contribute zero. Scores are
  relative to this run, not the official competition score. `environment.json`
  records revisions and machine information. Compare timings on the same runner.

Use `--sample 0` for all examples. Add `--large` for generated square fields of
side 256, 1024, and 4096 with three 4-by-4 cutters. These stress grid size and
route length, but do not replace irregular/holey examples. To compare another
checkout on the exact same inputs, repeat `--solver-root`, for example
`--solver-root merged=../merged/src/solver --solver-root proposed=src/solver`.
Install each checkout's solver environments first.

The original `eval-solver.py INSTANCES SOLUTIONS` command still validates saved
solutions, with no invented timing or memory measurements. It defaults to all
instances, or accepts `--sample 15` for the fixed benchmark set.

### PR reports

The benchmark workflow evaluates changed proposed solvers on the fixed 15
instances. It reuses a verified baseline from the latest `main` benchmark when
its solver fingerprint, instance manifest, evaluator, and configuration match.
Otherwise it measures the relevant merged solver. Its job summary and
downloadable `solver-benchmark` artifact contain the table and GIFs. The PR
comment contains the table, the tested commit SHA, and a link to the workflow
run, with one inline GIF for every solver-instance result that fits within
GitHub's comment-size limit. If that limit is reached, the comment says how
many rows were omitted and the complete report remains in the workflow
artifact. GIFs are publicly embedded from the repository's
`benchmark-assets` branch.
Manual workflow dispatches retain the `large` input, which adds the three
generated stress instances to both the manifest and the measured solver runs.
Solvers with other languages can expose the same Python CLI wrapper, but their
build dependencies must be installed before evaluation.

A separate `workflow_run` workflow updates one PR comment with the table and a
link to its workflow run. It must first be merged onto the default branch to run. It never
executes downloaded code, and uses only bounded, sanitized JSON fields in the
comment. Solver execution has a read-only token and no persisted checkout
credentials. Fork workflows may need a maintainer's first-run approval.
Reports are advisory because the PR can modify its own benchmark code.
GIFs are copied to the public `benchmark-assets` branch for inline PR images.
If the benchmark run fails or its artifact is unavailable, the PR comment says
so explicitly instead of presenting an empty result as a completed benchmark.
