# G-IMO-G9-FIVE-CORE-20261012 — Owner-designated exact HTML golden fixture

**Designation:** `OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT` per Owner directive **“save this as a golden fixture”** (2026-10-12 07:30:37 UTC). This freezes the specific five-role TEST HTML bytes from the integrated preview. It does **not** accept independent academic/QRT evaluations, authorize public release/merge, settle Core2A H3, or approve shared-printer A4.

## Exact golden files

| Core role | Frozen HTML |
|---|---|
| Core 1 orientation | [snapshots/core1.html](snapshots/core1.html) |
| Core 1A construction | [snapshots/core1a.html](snapshots/core1a.html) |
| Core 1B reconstruction | [snapshots/core1b.html](snapshots/core1b.html) |
| Core 2A supported application | [snapshots/core2a.html](snapshots/core2a.html) |
| Core 2B changed-demand transfer | [snapshots/core2b.html](snapshots/core2b.html) |

Source artifact: GitHub Actions [run 38215683516](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516), artifact ID `11732117118`, original TEST-only branch exact commit `f87d2f627e3f05476d39fb04d7f26e453661dc68`. Five frozen HTML blobs and **SHA-256** hashes are listed in [snapshot-lock.json](snapshot-lock.json), individually compared against original artifact before committing. Original render digest `ad02fef42f0d505a`, semantic digest `9497e294361663f2`, `render_core/2`, `PAGES`, held to `REFERENCE`, zero authored depth gaps. The old render digest is intentionally retained verbatim inside each frozen snapshot.

## Reproducible authored fixture

- [manifest.json](manifest.json): normal governed product manifest, five output roles `CORE1,CORE1A,CORE1B,CORE2A,CORE2B` with **`core2=[]`**; its `package_refs` points to the frozen [records.json](records.json) in this fixture, not a mutable TEST pilot.
- [records.json](records.json) git blob `cd5ef962f47808a05cfebec3a8a4f836ef0695cf`: byte-for-byte copy of the exact three-question **authored TEST** pilot used in the original integrated run; it inherits existing TEST SVG/teacher reference dependencies of that pinned renderer tree. No SOF/NCERT exam source question has been admitted.
- From the repo root, run `python Shared/tools/build_golden.py --id G-IMO-G9-FIVE-CORE-20261012 --check` to build from the **pinned records** without writing files, or omit `--check` to regenerate 6 pages (five roles + index) into the **gitignored** `rendered/` folder. Never replace `snapshots/` on routine rebuild.
- Regenerated files have a **different authority digest** because the golden fixture uses a distinct `manifest.json` and pinned `package_refs` path. This is expected and does **not** mean that the frozen reviewed pages changed. Rebuilding should preserve all five role structures/teaching moves while treating the committed snapshots as the canonical byte oracle. Any intended edit to frozen bytes requires a new Owner-directed version/fixture ID, fresh SHA-256 pins, and human review; do not mutate them implicitly.
- Automated lock check `tests/test_imo182_owner_golden_snapshot.py` asserts each frozen file matches `snapshot-lock.json`, selection/blueprint roles, and a structurally sound reference-depth regenerate with no gaps.

## Academic and delivery boundaries

The Owner designation relates to these exact five HTML artifact bytes. Prior Owner preview approval of the separate #187 Core1/Core2B files is a *different* hash scope. `QRT-JUSTIFY-D2` on authored Core2A/Core2B remains proposed; `D-182-2-H3` (potential early decisive proof hint) has no Owner decision recorded. QRT accepted numerator **0/28**. Real learner outcomes, exact ISO A4 linked print, authentic Core2 source custody, a public route, merge/release permissions, and independent academic blessing **are not conferred by golden snapshot archiving**. The three original split TEST draft PRs #186/#187/#188 remain independent until an explicitly authorized integration decision.

The purpose of this golden is to compare future Core page renderings against *the Owner-selected five-page learner experience*. Reference pedagogical technique descriptions remain in [TECHNIQUES.md](../../TECHNIQUES.md). Avoid treating exact HTML bytes or test-count success as proof of learner comprehension.
