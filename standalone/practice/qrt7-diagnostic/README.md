# G9O5-2a — Seven-Question Diagnostic Prototype (Newton's Laws · Touching Blocks)

Status: Prototype Delivery for Owner Trial (Benchmark B1).
Topic: Newton's Laws for Touching Blocks (`newtons-laws.contact-blocks`).
Level: D1 baseline (seven cognitive types, one question per type).

## Contents

- `index.html`: Fully self-contained diagnostic single-page application. Runs directly from `file://` with zero external network calls or CDN dependencies.
- `start-diagnostic.cmd`: One-command Windows launcher that opens `index.html` in Chrome.
- `G9O5-2a.question-bank.v1.json`: Exact snapshot of the Oracle question bank (7 items, D1 baseline).
- `README.md`: This documentation file.
- `tests/`: Automated browser verification suite testing real Chrome via Playwright over `file://`.
- `tests/shots/`: Directory for automated test screenshots (ignored by git).

## Fixed Rules Implemented

1. **Seven Fixed Questions, One Per Thinking Type at D1**:
   Delivery order: `APPLY` -> `SYNTHESIZE` -> `REPRESENT` -> `MODEL` -> `EXPLAIN` -> `JUSTIFY` -> `RETRIEVE`.
   Strategy/type cues and keys are kept hidden until the end review.
2. **Explicit "I cannot choose yet"**:
   Allows explicit unforced submission with `response_kind: "no_answer"` and `selected_option_id: null`.
3. **No Hints / No Mid-Test Solutions**:
   No countdown, no score target, no hints or right/wrong feedback are shown prior to final submission.
4. **Descriptive Timing**:
   Measures cumulative `active_ms` while the question view is visible and window is focused. Inactive / blurred time does not accumulate into `active_ms`. Tracks `wall_ms` elapsed view duration.
5. **Frozen Submission & 7-Row Review**:
   Submission freezes the attempt and presents all 7 questions with learner choices, reasoning, confidence, active time, correct keys, author explanations, and distractor tag hypotheses. Correctness is recorded as a raw observation without score replacement or mastery classification.
6. **28-Cell Topic Map Coverage**:
   Full 7 cognitive types × 4 levels (D1–D4). The 7 D1 cells carry linked response evidence; 21 remaining cells are explicitly marked `unassessed` with empty evidence arrays.
7. **JSON Export & Reopening**:
   "Save my diagnostic" downloads a UTF-8 JSON file conforming to the contract. The built-in JSON inspector and file reopening component allow inspecting and verifying previously saved records.

## Quick Launch

Double-click `start-diagnostic.cmd` or execute:

```cmd
.\start-diagnostic.cmd
```

## Running Browser Tests

Tests use the system Chrome via global Playwright:

```powershell
$env:NODE_PATH = (npm.cmd root -g)
node standalone/practice/qrt7-diagnostic/tests/diagnostic-demo.spec.js
```
