# First JEE Main intake pilot — Work, Power and Energy

Prepared 27 October 2026. Proposed implementation brief; not issued, built or run.

## Outcome and starting material

Improve the existing local harvester sufficiently to return a small faithful JEE Main Paper1 Physics PYQ candidate packet for Work, Power and Energy. Search years2025–2026; ten candidates maximum for the first demonstration. These are source years, not the learner's deferred target year. The learner is Grade10, targeting JEE Main.

Start at [ExamSIDE Work Power & Energy](https://questions.examside.com/past-years/jee/jee-main/physics/work-power-and-energy). Oracle followed ten distinct question links and inspected their current question blocks. [candidates.json](candidates.json) contains exact URLs, publisher-claimed date/shift, format, concept summaries and observed gaps. It is a discovery manifest, not a canonical bank or independently verified set of exam questions.

| ID suffix | Source date/shift | Why include it |
|---|---|---|
|001|21Jan2026 morning|Potential-energy graph to force; authentic figure needed.|
|002|22Jan2026 evening|Conservative-force statements; missing formula changes meaning.|
|003|6Apr2026 morning|Gravity plus resistive work; sign and numerical givens matter.|
|004|5Apr2026 evening|Static-friction work during assembly motion; displacement/frame matters.|
|005|7Apr2025 evening|Short force-category MCQ; a usable text extraction reference case.|
|006|7Apr2025 morning|Time-dependent force and power; initial conditions must be preserved.|
|007|4Apr2025 evening|Oblique pull and friction; angle and normal-force dependence matter.|
|008|29Jan2025 evening|Sand conveyor; mass-flow relation and power accounting matter.|
|009|28Jan2025 morning|Hoop plus spring; symbolic geometry and original figure are essential.|
|010|23Jan2025 morning|Numerical variable-force work; path constraint and endpoints are essential.|

This is a deliberately varied extraction trial. It establishes no ranking, full chapter coverage, ten distinct QRT cells or learner weakness profile.

## Scope for the Owner-assigned implementer

Working location to confirm: `<harvester-repository>`. Existing skill: `.agents/skills/olympiad-web-harvester`. Confirm actual repository controls, writer custody and permitted return route before dependent edits. No implementation changes are included in this packet.

Reuse the [general JEE Main discovery design](JEE-MAIN-DISCOVERY.md) and [source-bound skill review](HARVESTER-REVIEW.md). Keep this first implementation small: discovery plus faithful candidate extraction, the helper corrections needed by this route, and a reproducible return. Preserve other exam workflows and local-only custody. Do not edit accepted NLM B2 files, canonical source banks or shared academic vocabularies as an incidental part of this pilot. No remote push, merge or deployment is part of it.

1. Add the JEE Main source profile to the existing source registry and route the skill to the relevant workflow. Follow observed question/PDF links; max30 new pages for the pilot, cache repeated sources and report consumed scope. Use a supported browser only where actual rendering is needed. Never invent a selector or private endpoint.
2. Capture original source evidence privately. Recover original math from the page's actual representation or a linked paper; ordinary text extraction demonstrably loses equations here. Capture actual question figures and distinguish them from solution images.
3. Scope extraction to the current question block. These pages include following questions and navigation; they must not be concatenated into the current item. Repeated “Correct Your answer” accessibility text appears under every option and is not a reliable key. Candidate005 has an explicit named answer in its explanation, but that is still a publisher key.
4. Preserve both single-answer MCQ and numerical formats. Fix multiline/parenthesized option handling, repeated-label ambiguity and radical grouping where relevant. Read actual bank `stem`/ID structures when building the duplicate index; fail/incomplete on zero usable indexed texts or parse errors instead of passing a demonstration.
5. Match official papers/final keys where available, using exact paper/date/shift and question identity. [NTA](https://jeemain.nta.nic.in/) and [MathonGo's paper index](https://www.mathongo.com/iit-jee/jee-main-previous-year-question-paper) are corroboration starting points; this packet does not claim any completed official or cross-publisher match. Retain unmatched/conflicting cases explicitly.
6. Bind a successfully extracted instance to a selected Common demand/band template and actual topic adapter. Reuse the seven existing demands. Candidate005 has only an Oracle-proposed RETRIEVE-D1 fit; its adapter binding and independent fit/science check remain unresolved. Do not force other items into MODEL/D4 or fabricate a completed adapter. Preserve authored teaching/diagnosis suggestions separately from source text and from observations of actual learner work.

## Known contrary cases from real discovery

- Several WPE URLs contain `units-and-measurements` in their slugs. Topic classification must follow the source context/content, not that slug.
- Publisher title numbers, chapter ordinals and image-caption question numbers differ. None may silently become an official NTA question ID.
- Nine selected text captures are incomplete; silently accepting their stripped text would lose essential data. Treat them as recovery work or explicit unresolved cases.
- The current text reader captured candidate005's stem, all four options and an explicit publisher key. Its absence of complicated math makes it a useful baseline, but it does not validate the other extraction paths.
- Candidate006's publisher solution assumes an initial velocity; recover the actual source givens and retain any ambiguity instead of adding that condition to the question.

## Return and acceptance

Return the exact changed skill/helper files or a patch, the pilot command/config, a machine-readable candidate packet in the existing consumer shape, original evidence locators/hashes, a coverage report and actual check outputs. A suggested private output location is the implementer's own `scratch/intake/wpe-pilot-2025-2026/`; the actual approved transfer/return route must be resolved before exchange. The Owner confirms actual artifact access and return custody when assigning the implementer.

Every attempted candidate must appear as fully extracted or explicitly unresolved with a concrete reason. Include at least the observed text-baseline case and a real recovered mathematical/figure case; a URL list alone does not prove the skill works. Exercise duplicate-index coverage, actual CLI behavior, multiline/parenthesized options, changed signs, math grouping and unresolved-figure handling with isolated fixtures. Show one genuine Common-template/adapter binding if available; otherwise return the exact missing adapter input as unresolved rather than claiming composition.

Report extraction fidelity, official-key matching, scientific correctness, QRT fit and rendered behavior separately. Tests do not establish all of these at once. Owner may inspect the draft; required distinct academic checking precedes learner use. Do not publish, mark canonical acceptance or infer a learner profile from this intake trial.


## Current status

Ten pages inspected; one short text-only stem/options/publisher-key reference captured. Nine need original math or figures. Source bytes, official matching, completed adapter bindings, skill implementation and independent academic checks remain pending. The Owner assigns the actual implementer.
