# Oracle review — olympiad-web-harvester

27 October 2026. Historical assessment of the external harvester; source fingerprints and observed outputs are preserved in the companion probe receipt.

Reviewed the six files under `<harvester-repository>/.agents/skills/olympiad-web-harvester`, relevant local Shared contracts and two bank structures. Executed isolated synthetic helper probes and a read-only load of the real deduplication index. The six reviewed file hashes and actual outputs are in [helper-probes.json](helper-probes.json).

This is an Oracle assessment of an upstream skill, not independent certification of its question banks. The reviewed skill, source banks and accepted B2 prototype were not edited. No live harvesting or agent launch occurred during that review. Source URLs/selectors were not tested against live websites. The first probe run encountered a sandbox temporary-directory cleanup error; the probes were rerun successfully using the authorized workspace. No result below depends on that failed run.

## Design call

Keep the skill as a source-intake capability, but change its output from automatically promoted question banks to traceable, reviewable question-instance candidates. Its current claims of semantic deduplication, 28-cell mapping and fully audited output exceed what its contracts and helpers establish.

The upstream purpose is to supply useful instances for:

`Tile(topic, demand, band) = Common blueprint(demand, band) + Topic adapter(topic)`

A harvested question can become an instance inside that tile. It is not itself a reusable Common blueprint, a topic adapter, evidence that the learner has a weakness, or proof that a cell is fully covered. Multiple questions can belong to the same cell while testing different conceptual decisions.

## Prioritized findings

### 1. P1 — The skill substitutes a different QRT taxonomy

`.agents/skills/olympiad-web-harvester/SKILL.md:149` defines six demands: MODEL, JUSTIFY, SYNTHESIZE, GENERALIZE, CLASSIFY and VERIFY. Six demands by four bands give 24 cells, despite the repeated 28-cell claim. `.agents/skills/olympiad-web-harvester/references/agent_prompts.md:50` repeats the substitution.

The local repository already has the Owner's seven demands in `Shared/vocabularies/cognitive-demand.v1.json`: RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE and JUSTIFY. It also has 28 demand-specific templates in `Shared/quality/question-demand-templates.v1.json`, derived from its matrix. The skill's fixed X=givens, Y=invariant, Z=deductive link, W=proof closure also replaces these demand-specific meanings with a proof-oriented pattern.

**Change:** reference the existing vocabulary, band policy and selected template by version. Record the actual learner-owned crux and why it fits one primary demand. Use the existing canonical crux reference where the consumer requires it; do not create a competing crux field. GENERALIZE, CLASSIFY and VERIFY may describe particular actions, but must not become substitute primary-demand enums. Do not repair every computational question merely by renaming CALCULATE to MODEL: executing a supplied procedure can correctly be APPLY.

The skill's Olympiad labels and numerical D-band ranges must not replace the shared rubric. An exam's Achievers label alone cannot establish D4, and a difficult calculation alone cannot establish MODEL. An intended tag and a checked tag are separate facts; retain UNCERTAIN when the fit is unresolved.

### 2. P1 — The real deduplication index contains no usable question text

`.agents/skills/olympiad-web-harvester/scripts/deduplicator.py:51` reads `question_id` and `question_text` for Mathematics; the inspected Mathematics bank uses `id` and `stem`. The inspected Physics bank uses `question_id` and `stem`, so its text is also missed.

The actual engine loaded **882 entries, zero nonempty question texts, zero nonempty token sets and 654 UNKNOWN IDs**. Missing files, malformed JSON and schema errors can also be hidden by broad exception handlers. An apparently populated index therefore provides no effective comparison.

The advertised `deduplicator.py --check-duplicates` command ignores that argument and runs a single hard-coded demonstration. It exited 0 and reported no candidate match against this empty-text index. That is not a batch duplicate check.

**Change:** use explicit readers for the actual bank schemas and preserve source path plus stable ID. Report files inspected, questions read, questions indexed, exclusions and errors. An empty/unusable expected index must produce an explicit incomplete/failure result. Implement a real batch CLI with input locators, machine-readable findings and meaningful exit codes; the documented invocation must exercise that CLI.

### 3. P1 — Similarity removes mathematical meaning

`.agents/skills/olympiad-web-harvester/scripts/deduplicator.py:20` strips operators and drops one-character variables/numbers. Observed results:

| Inputs | Similarity | Problem |
|---|---:|---|
| `Find x + y = 2.` versus `Find x - y = 2.` | 1.0 | Opposite operations become indistinguishable. |
| `x + y = 2` versus the identical expression | 0.0 | Both token sets are empty, so an exact copy is missed. |
| Charge −12 coulombs versus +12 coulombs | 1.0 | Physically meaningful signs disappear. |

The code performs lexical token overlap, not established semantic equivalence. It does not implement the claimed Levenshtein calculation. Thresholds also disagree: 0.82 in the diagram/prompt/code versus 0.85 in the prose decision rule.

**Change:** separate exact copies, lexical similarity candidates, same-family variants and substantively different demands. Preserve mathematical structure, options, figure identity and conditions. Use similarity to retrieve possible matches, not to authorize automatic deletion or NEW CANONICAL status. A changed number can be same-family practice; a changed assumption may be a valuable boundary instance even with high textual overlap. Declare one calibrated threshold policy and retain reviewed decisions with evidence.

### 4. P1 — Parsing and normalization can change or lose the question

Observed in `.agents/skills/olympiad-web-harvester/scripts/latex_sanitizer.py`:

- `AB = &radic;50 cm` becomes `AB = \\sqrt50 cm`: radical grouping is not preserved.
- A simple one-line four-option question works, but the same options on separate lines return an empty options dictionary.
- Options containing `(x+1)` and `(x-1)` are not parsed.
- Repeated C labels overwrite each other and return only three distinct options rather than an explicit ambiguity.
- `Choose point A. Now solve.` is truncated to `Choose point` when followed by four options: prose `A.` is mistaken for an option boundary.
- Currency dollars remain unchanged; math symbols introduced into prose are not put into math mode. A mixed one-sided whitespace example is changed across the closing/opening delimiters instead of cleanly normalizing each math span.

**Change:** retain immutable raw content and source locations, then parse with a source-specific layout reader. Separate span-aware math normalization from option extraction. Preserve mathematical operands/grouping; flag ambiguity rather than guessing. Verify unique labels and complete content before accepting an MCQ. Retain unsupported/open/numerical-answer formats as explicit unparsed or supported-format records; do not silently force every question into four choices. Save a raw-to-normalized diff and unresolved fragments.

### 5. P1 — A fabricated figure can silently become academic truth

`.agents/skills/olympiad-web-harvester/SKILL.md:127` instructs automatic SVG generation when a figure is missing. But a missing diagram can contain information absent from the text. A generic triangle or plausible mechanics scene cannot recover that information.

The generator's default is an arbitrary triangle. It does not validate geometric constraints. Its metadata is interpolated without XML escaping: `Force A & B` / `x < y` produced malformed SVG. Custom elements with 8px text pass through despite the claimed enforced 14px floor. Accessibility attributes alone do not establish readable, correct diagrams across themes or rendered sizes.

**Change:** prefer the authentic source figure. If unavailable, mark the item UNRESOLVED_FIGURE. A reconstruction needs a complete explicit constraint specification and a separate semantic check; identify it as an authored reconstruction. Preserve source-figure versus reconstruction provenance and prevent unresolved geometry from entering a trusted bank. Validate XML, inspect allowed element content, measure rendered readability and check the represented entities/relations. Avoid decorative fallback figures presented as the source scene.

### 6. P1 — The handoff lacks source-to-tile bindings and protected-work checks

The current metadata records a URL/filename and broad exam fields, but not enough to distinguish a faithful source extraction, the agent's solution, an inferred answer, an authored distractor explanation, or a rebuilt figure. It does not identify the Common cognitive blueprint and topic adapter used for a resolved instance.

The existing local `BP-CORE2-SOURCE-QUESTION@1.11.0` does exist, but it is the presentation/support blueprint. Naming it does not establish a correct cognitive-cell composition. Its actual policies prohibit generic filler support, untracked pre-attempt assistance and support that reveals protected work. The skill instead requires three hints for every question and defines Tier 3 as the decisive crux move. A button lock alone cannot protect the decision once that hint is opened.

**Change:** bind each candidate to the selected demand/band template, topic adapter, concept and learner-owned crux. Record criteria and the evidence a response would need to show; keep any misconception or repair a hypothesis until an actual response supports it. Link suggested teaching to an existing adapter repair only when that binding is justified. Do not infer topic-wide weakness from a question tag or chosen distractor alone.

Author support only where useful, label source versus authored support, and distinguish orientation from assistance that changes the assessed act. A final crux disclosure belongs in an explicitly assisted/full-solution state. Preserve support exposure when later learner evidence is saved. Core2B transfer additionally needs a specified changed demand relative to prior exposure; new numbers or a D4 badge do not establish transfer. The intake skill can supply source instances for Core1 teaching/reconstruction work, but it must not claim it has generated those complete lessons merely by harvesting Core2 questions.

### 7. P2 — Validation, custody and reviewer responsibilities are overstated

`.agents/skills/olympiad-web-harvester/SKILL.md:191` lists generic success gates rather than exact candidate coverage. The referenced typography auditor currently selects three named Mathematics banks and two master-suite HTML files, skipping absent targets. It does not automatically validate a newly staged batch. `standalone_conformance.py` requires a page or `--governed`; the documented no-argument command is incomplete. Its default exit behavior also needs to be understood before claiming an enforcement result. These tools were inspected, not run as a complete bank/UI audit in this review.

Four choices contain three distractors when there is one correct answer; the request for four diagnostic distractors is inconsistent. Authentic source options must be preserved even if their diagnostic purpose is uncertain. Agent 2 both authors support and verifies it, which does not establish a distinct check of its own authored claims. A second derivation by the same author is valuable corroboration, not automatically an independent reviewer verdict.

**Change:** have each check name exact inputs, coverage, failures and NOT_RUN scope. Keep extraction fidelity, scientific solution correctness, QRT fit, figure fidelity, browser behavior and Owner acceptance as separate results. Use an actual non-author for the required final academic check, without mandating an unnecessary fixed agent chain. Keep the existing local-only custody rule. Promotion/commit/publication must use the actual Owner-authorized writer and destination; a prompt does not grant that authority. Public/standalone byte parity is useful only where those mirrors are intended deliverables; it proves neither extraction fidelity nor academic correctness.

## Recommended upstream handoff

Reuse the consumer's existing schemas instead of creating another competing bank format. The handoff needs these meanings, whether represented in the bank itself or a linked candidate manifest:

| Layer | What to preserve |
|---|---|
| Source evidence | Original URL and downloaded-byte hash; acquisition time; paper/section/original question number; PDF page/crop or HTML locator; original figure and source key/solution if supplied. |
| Extracted instance | Stable instance ID; immutable raw stem/options and normalized counterparts; assets; extraction warnings and unresolved content. Keep source-provided and agent-authored material distinguishable. |
| Tile binding | Topic/concept; one primary demand and band with cited rubric/version; intended versus checked fit; actual Common template and adapter references; learner-owned crux and observable criterion. Unbound candidates remain unbound. |
| Teaching potential | Relevant why, conditions/boundaries, common wrong reasoning and existing repair references. These are authored hypotheses/material until reviewed and tied to learner evidence. |
| Match and review evidence | Candidate duplicate/variant links and reasons; scoped extraction/science/fit/figure assessments; exact reviewed versions; remaining uncertainty. |

For example, a source problem that explicitly supplies Newton's law and asks for substitution may be APPLY. One that leaves static-versus-sliding model choice to the learner may be MODEL. Explain the distinction from the actual source task; do not alter the source question just to occupy a desired cell. If a teaching adaptation is useful, preserve it as a separately identified authored variant with its own fit assessment.

## Smallest useful improvement trial

Use one authentic available source paper and a small set of questions, with one intended tile chosen from the existing seven-demand matrix. JEE Main remains the learner's target; SOF/other Olympiad provenance should remain truthful and its relevance to the chosen concept explicit.

1. Preserve the paper, source question locations and original figures. Account for every attempted item as parsed or explicitly unresolved.
2. Demonstrate a faithful source instance with a resolved Common-template/topic-adapter/crux binding. Do not claim the whole tile is covered.
3. Add isolated contrary fixtures: multiline options, parentheses, duplicated labels, a prose `A.`, a radical, a missing figure, an exact copy, a changed sign and a same-family numeric variant.
4. Show the repaired deduplication reader indexes actual nonempty texts and stable IDs; malformed banks or zero useful indexed items must be visible failures/incomplete results.
5. Check one complete candidate and its support against the source and selected rubric. Preserve an explicit unresolved case. Obtain the required distinct academic check before learner use; the Owner can inspect the draft first.

The useful return is a small trustworthy candidate packet plus the actual check receipt. No new diagnostic loop, automatic learner grading, complete 28-cell bank, large crawl or additional platform is needed to prove this upstream improvement.


## Publication scope

This preserves the earlier assessment and observed helper results. The external skill sources are not included; source fingerprints identify the reviewed versions. Repairs and bank certification remain pending. The selected first topic is Work, Power and Energy; see [the builder brief](BUILDER-BRIEF.md).
