# G9O5-3 / P2 — Diagnostic to Guided Learning Loop Prototype

## Overview
This directory contains the G9O5-3 / P2 prototype: a self-contained, browser-executable learning loop bridging an unassisted diagnostic observation to a focused guided lesson and a fresh same-cell re-check.

Target learner: One Grade 10 student preparing for IIT JEE (deferred exam year).
Topic: Newton's Laws for Touching Blocks (`newtons-laws.contact-blocks`).
Level: D1.

## Artifacts Delivered
- `index.html`: Complete standalone web application. Operates over `file://` protocol with zero CDNs, zero external dependencies, and zero console errors.
- `start-learning.cmd`: Automated Windows batch launcher to launch the prototype directly in Google Chrome.
- `P2.learning-unit.v1.json`: Snapshot of the Oracle G9O5-3 pilot learning unit contract.
- `G9O5-2a.question-bank.v1.json`: Snapshot of the Oracle P1 diagnostic question bank contract.
- `tests/learning-demo.spec.js`: Automated Playwright test suite exercising real system Chrome.
- `tests/shots/`: Directory for automated browser verification screenshots.

## Architecture & Workflows

### 1. Dual Entry Points
- **Start a new diagnostic**: Seven-question unassisted diagnostic covering all 7 QRT cognitive types at level D1. Incorporates the G9O5-2a design amendment: reasoning ("How did you decide? (optional)") is optional for all confidence levels, including Sure. Blank reasoning never blocks navigation or submission.
- **Open saved diagnostic or P2 session**: Accepts genuine P1 v1.0 diagnostic export JSON files, v1.1 diagnostic export files, or v2.0 P2 learning session files. Computes and records the SHA-256 hash of the parent record bytes, keeping original responses intact.

### 2. Seven-Type Evidence Profile
- Displays 7 observed evidence rows with strict profile groundings:
  - `Correct and sure — one question`
  - `Correct, unsure`
  - `Correct, guessed`
  - `Needs practice` (with confidence displayed separately)
  - `Not assessed yet` (for no-answer)
- Learner reasons are displayed verbatim or flagged as `Not recorded (omitted)` or `Not recorded (placeholder)`.
- Distractor tags and interpretations are explicitly displayed as hypothetical possibilities.
- For `EXPLAIN` and `JUSTIFY`, selecting correct options without reasoning is explicitly tagged as demonstrating recognition only.
- 28-cell coverage grid tracks 7 assessed D1 cells and 21 unassessed cells (D2–D4). Never auto-promotes or declares mastery.

### 3. Guided Pilot Lesson (SYNTHESIZE D1)
- Worked problem: Blocks A (2 kg) and B (3 kg) pushed rightward with 20 N on a frictionless surface.
- 4 interactive stages:
  1. `whole`: System boundary selection ($a = 20 / (2+3) = 4\text{ m/s}^2$).
  2. `part`: Isolating B to find contact force ($C = 3 \times 4 = 12\text{ N}$ right, reciprocal on A is 12 N left).
  3. `distinguish`: Explicitly distinguishing contact force (12 N) from A's net force ($20 - 12 = 8\text{ N}$).
  4. `explain`: Reconstructing the route with equations hidden, capturing explanation attempts as guided learning before revealing comparison feedback.

### 4. Fresh Same-Cell Re-Check
- Fresh problem: Blocks A (3 kg) and B (2 kg) with 35 N rightward push.
- Strictly unassisted: No hints, formulas, or intermediate values before commitment.
- First committed answer recorded as independent evidence.
- Correct answer: 14 N to the left (Option C).
- Post-commit feedback reveals full explanation and distractor hypotheses.
- Solution-exposed retries are explicitly marked as `practice` and never overwrite the original fresh check.

### 5. Linked Session Record (v2.0 JSON)
- Downloads structured JSON linking parent diagnostic evidence, guided stages, fresh re-check result, and the updated 28-cell coverage map.
- Can be reopened at any time via Option 2 on the entry screen.

## How to Launch
Double-click `start-learning.cmd` or execute:
```cmd
.\standalone\practice\qrt7-learning\start-learning.cmd
```

## How to Test
Run the Playwright test suite using the global Playwright package and real Google Chrome:
```powershell
$env:NODE_PATH = (npm.cmd root -g); node standalone/practice/qrt7-learning/tests/learning-demo.spec.js
```
Also verify P1 suite remains fully passing:
```powershell
$env:NODE_PATH = (npm.cmd root -g); node standalone/practice/qrt7-diagnostic/tests/diagnostic-demo.spec.js
```
