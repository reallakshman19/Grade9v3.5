# R14 CORE1A component structural golden — v2 PRACTICE

Owner decision **AB-R14-PRACTICE**, 15 October 2026 18:28 Asia/Muscat: retain `PRACTICE_LINKS` in the renderer. It represents a deliberate authored-practice route from the Core1A concept to the selected Core2A exercise, not an unapproved replacement of original question text or a mathematical acceptance claim.

This **new, review-only fixture** is derived from frozen source-commit `40142fe06818e7a946d6296911d495f3f3323b12` and historical golden `G-IMO-G9-FIVE-CORE-20261012`, whose bytes and immutable snapshot lock remain untouched.

The four snapshots CORE1, CORE1B, CORE2A and CORE2B are byte-identical to the old golden. CORE1A has exactly one additional empty, marker-only `<div data-g9-component="PRACTICE_LINKS"></div>` inserted immediately before the former `LEARNING_TRANSITIONS` component (zero-based ordinal 11), without editing a question, answer, role, slot, block, teaching statement, or any other source HTML. This is a **structural marker contract**, not a fabricated full candidate HTML snapshot.

Historical R8 checks continue to use the old golden. Only an explicitly flagged R14 native comparator may select this version, after confirming the old lock, the new lock hash and exact one-component-only byte delta. All other structural checks remain strict.

No independent academic review, Owner QRT acceptance, source rights, release, merge, or publication is granted. Seven source-held cases remain held; academic/Owner accepted 0.
