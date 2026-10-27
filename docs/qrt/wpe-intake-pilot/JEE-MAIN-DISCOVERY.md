# Extend the harvester for JEE Main previous-year questions

Design brief, 27 October 2026. Proposed capability; implementation and execution pending.

## Outcome

Given an exam, subject, topic and year range, discover relevant JEE Main Paper1 (B.E./B.Tech.) previous-year questions, then extract a small selected batch with faithful source evidence. Supply question instances that can be bound to a Common blueprint and topic adapter. Keep JEE Main, JEE Advanced, other exams, mock questions and PYQs distinguishable.

Add this capability to the existing harvester rather than rewriting all earlier Olympiad workflows. Its current entrypoint can route to a JEE Main reference when that task is requested. The source registry belongs in the existing `references/target_patterns.json`; keep active-source configuration in one place. Site-specific reading code should implement the same small candidate interface.

## Verified starting sources

These pages were checked through web search/open on27October2026. Discovery paths were verified; CSS selectors, private APIs and end-to-end extraction were not verified or invented.

| Source profile | Starting locations | Intended job |
|---|---|---|
| ExamSIDE | [Chapter-wise JEE Main](https://questions.examside.com/past-years/jee/jee-main), [paper-wise JEE Main](https://questions.examside.com/past-years/year-wise/jee/jee-main) | Discover by subject/chapter or year/date/shift, then follow actual paper/question links. |
| NTA | [JEE Main official site](https://jeemain.nta.nic.in/), [example final Paper1 answer-key document](https://jeemain.nta.nic.in/document/final-answer-key-for-jeemain-2025-session-2-paper-1-b-e-b-tech/) | Prefer available official papers and final answer keys for source corroboration. The homepage currently exposes2026 B.Tech paper links. Do not assume all years are available there. |
| MathonGo | [Previous-year paper index](https://www.mathongo.com/iit-jee/jee-main-previous-year-question-paper) | Discover alternative paper PDFs by year/date/shift and corroborate source availability. Preserve publisher provenance. |

ExamSIDE's homepage redirects to `questions.examside.com`; use the observed question-site URLs. NTA document downloads may resolve to a different host through links on the official site: preserve that link chain instead of guessing download URLs or rejecting an authentic linked CDN.

Adding another IIT-JEE site requires a small source profile and a tested sample extraction. Do not assume ExamSIDE selectors work on other websites.

## Two modes

### DISCOVER

Input example, illustrative configuration rather than a new canonical schema:

```yaml
exam: JEE_MAIN
paper: PAPER_1_BE_BTECH
subject: Physics
topic: Work, Power and Energy
topic_aliases: [work-energy theorem, potential energy, power]
years: [2025, 2026]
sources: [examside, nta, mathongo]
max_candidate_questions: 10
max_pages_to_open: 30
```

Start with known source indexes. Follow observed chapter, paper and question links, keeping a visited-URL set, a bounded request budget and a cache. Topic-first discovery finds concept candidates; paper-first discovery establishes date/shift identity and helps identify omissions. Neither path alone proves complete coverage.

Use web search to find missing paths or new sources, for example:

```text
site:questions.examside.com/past-years/jee "JEE Main" "Work, Power and Energy"
site:questions.examside.com "JEE Main 2025" "work energy"
site:mathongo.com/iit-jee "JEE Main 2025" "question paper"
site:jeemain.nta.nic.in "2025" "final answer" "Paper-1"
```

Search snippets identify candidate URLs; they are not the extracted question or proof of authenticity. Open the source and record what is actually present. Year range is a run input, separate from the learner's still-deferred target exam year.

Discovery output: source URL, discovered-from URL, source title, claimed exam/paper/year/date/shift/subject/topic, available question/PDF links, and unresolved metadata. Do not silently infer missing shift, session or question identity.

### HARVEST_CANDIDATES

Take selected discovery records. A source adapter reads the observed public HTML structure or linked PDF; use a supported browser only if the actual page requires rendering. Do not guess selectors or hidden endpoints. If access is unavailable, record it and use another available source.

For PDFs, preserve the original downloaded bytes and locate each question by page and question number, including the associated figure/crop. Use OCR only where needed and retain its uncertainty. For HTML, preserve the source locator, math content, original image links and the fetched evidence needed to check extraction.

Support both MCQ and numerical-answer questions. Keep units, signs, intervals, fractions, radical grouping, options, diagrams and answer conditions. Distinguish the source answer/key/solution from an agent-authored derivation. Missing figures or uncertain option boundaries remain unresolved; never substitute a plausible generic figure.

Return traceable candidates, not automatically accepted canonical bank entries. Use the existing consumer schemas and stable IDs; a linked intake manifest can retain extraction and matching evidence without inventing a competing academic schema.

## Verification and QRT binding

Where an official paper/key is available, match exact exam, paper, session/date/shift and official question/option identity where supplied. Option letters or a question number alone are insufficient when editions/orderings differ. Record matches, mismatches and not-verified cases explicitly. Preserve final versus provisional key identity and any source-recorded dropped/multiple-answer status; do not silently choose between disagreeing keys.

An accessible third-party solution can help a derivation check, but does not become an NTA-authored solution. Reuse an existing source question across mirrors through source-occurrence links. Cross-site identity is stronger than a loose stem-similarity score; changed signs, assumptions, figures and options must remain visible.

Only after source fidelity is established, propose one primary demand from the existing seven-demand vocabulary and a D-band from its shared rubric. Bind the actual learner-owned crux to the selected template and topic adapter, with intended/checked fit and uncertainty separate. A chapter label does not establish MODEL or D4. A numerical question may correctly be APPLY. If no suitable adapter exists, mark the binding unresolved rather than claiming the tile is composed.

The upstream product is a question instance with source evidence and a proposed tile binding. The Common blueprint supplies the thinking contract; the topic adapter supplies concept truths, conditions, representations and justified teaching/repair mappings. Harvested item count is not a measure of complete tile coverage or a learner weakness profile.

## Pilot and done-when

Start with Physics / Work, Power and Energy /2025–2026, at most10 question candidates and30 opened pages. These are pilot search years, not a changed learner target year. Expand subject/year coverage only after this small return is useful.

The return must include:

1. Actual discovered URLs and enough source evidence to open/check each selected question, including exam identity and original figures.
2. One complete parsed instance, MCQ/numerical format handling where encountered, and every failed/ambiguous attempted item accounted for.
3. Cross-source or official corroboration where available, with unmatched cases explicitly not verified. Do not manufacture a second source match to meet a count.
4. One justified QRT/template/adapter binding and a candidate rejected or left unresolved for a concrete fidelity/fit reason.
5. Reproducible check outputs naming exact candidate inputs and coverage. Preserve local-only custody; no remote bank publication is part of this brief.

The previously demonstrated helper defects must be corrected for the relevant pilot path: the real deduplication reader must index nonempty stems/stable IDs, and extraction must preserve multiline/parenthesized options and mathematical grouping. `--check-duplicates` must perform an actual check rather than the existing hard-coded demo. See [the review](HARVESTER-REVIEW.md) and [observed probes](helper-probes.json). The Owner may inspect a draft; required distinct academic review still precedes learner use.
