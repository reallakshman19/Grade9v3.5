#!/usr/bin/env python3
"""Opt-in, fail-closed draft HTML round-trip adapter for held IMO TEST assets.

Never touches public/, docs/, academic packages, release receipts, or accepted
products. Output is for local candidate/QA inspection only, not publication.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Shared.tools.imo_roundtrip_contract import audit  # noqa: E402


class AdaptationError(ValueError):
    pass


def _html_article(html: str, *, qid: str, role: str) -> str:
    """Do not rewrite anything unless one matching renderer article exists."""
    articles = re.findall(r'<article\b[^>]*>.*?</article>', html, re.S)
    matches = [a for a in articles if re.search(r'\bid="' + re.escape(qid) + r'"', a.split('>', 1)[0])
               and re.search(r'\bdata-g9-role="' + re.escape(role) + r'"', a.split('>', 1)[0])]
    if len(matches) != 1:
        raise AdaptationError(f'{role}: expected one exact rendered article')
    return matches[0]


def _replace_tag_attribute(tag: str, name: str, expected: str, updated: str) -> str:
    needle = f'{name}="{escape(expected, quote=True)}"'
    if tag.count(needle) != 1:
        raise AdaptationError(f'{name}: expected original attribute not found once')
    return tag.replace(needle, f'{name}="{escape(updated, quote=True)}"', 1)


def adapt(package: dict, manifest: dict, pilot: dict, practice: str, concept: str,
          *, package_ref: str | None = None) -> tuple[str, str, dict]:
    before = audit(package, manifest, pilot, practice, concept, package_ref=package_ref)
    identity_errors = set(before['errors'])
    allowed = {
        'REPAIR_TARGET_NOT_EXACT_STEP',
        'REPAIR_HREF_NOT_EXACT_STEP',
        'CORE1A_STEP_NOT_ADDRESSABLE',
        'CORE1A_EXACT_CORE2A_RETURN_MISSING',
    }
    if not identity_errors <= allowed:
        raise AdaptationError('unrecognised/mismatched candidate or protected gate: '
                              + ','.join(sorted(identity_errors - allowed)))
    qid, mic, step = before['question_id'], before['microtopic_id'], before['repair_step_id']
    if not all(isinstance(k, str) and k for k in (qid, mic, step)):
        raise AdaptationError('missing selected candidate identity')

    question_article = _html_article(practice, qid=qid, role='CORE2A')
    concept_article = _html_article(concept, qid=mic, role='CORE1A')
    repair_openings = re.findall(r'<a\b[^>]*\bdata-g9-repair-ref="' + re.escape(escape(step, quote=True))
                                 + r'"[^>]*>', question_article, re.S)
    if len(repair_openings) != 1:
        raise AdaptationError('missing or duplicate exact repair anchor')
    old_tag = repair_openings[0]
    old_href = re.search(r'\bhref="([^"]*)"', old_tag)
    old_target = re.search(r'\bdata-g9-repair-target="([^"]*)"', old_tag)
    if not old_href or not old_target:
        raise AdaptationError('missing renderer repair target')
    # It must point to a local Core1A unit, never an arbitrary URL or test site.
    if not re.fullmatch(r'core1a\.html#[A-Za-z0-9_-]+', old_href.group(1)):
        raise AdaptationError('unsafe original Core1A URL')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', old_target.group(1)):
        raise AdaptationError('unsafe original construction id')
    new_tag = _replace_tag_attribute(old_tag, 'data-g9-repair-target', old_target.group(1), step)
    new_tag = _replace_tag_attribute(new_tag, 'href', old_href.group(1), 'core1a.html#' + step)
    new_question_article = question_article.replace(old_tag, new_tag, 1)
    practice = practice.replace(question_article, new_question_article, 1)

    # The renderer currently uses <li data-g9-step="TC-02"> with no id. Turn
    # this exact teaching item into a fragment target, not the entire unit.
    step_matches = re.findall(r'<li\b[^>]*\bdata-g9-step="' + re.escape(escape(step, quote=True))
                              + r'"[^>]*>', concept_article, re.S)
    if len(step_matches) != 1:
        raise AdaptationError('cannot locate exactly one authored teaching step')
    old_step = step_matches[0]
    if 'id="' in old_step:
        if not re.search(r'\bid="' + re.escape(escape(step, quote=True)) + r'"', old_step):
            raise AdaptationError('authored teaching step has conflicting id')
        new_step = old_step
    else:
        new_step = old_step[:-1] + f' id="{escape(step, quote=True)}">'
    new_concept_article = concept_article.replace(old_step, new_step, 1)

    # Add one precise, explicitly assisted return path. This is NOT an
    # independent/unseen attempt, and does not clear or award attempt credit.
    return_link = (
        '<p class="g9-imo-held-return" data-g9-held-roundtrip="assisted-only">'
        f'<a data-g9-practice-link data-g9-concept-ref="{escape(mic, quote=True)}" '
        f'data-g9-question-ref="{escape(qid, quote=True)}" '
        f'href="core2a.html#{escape(qid, quote=True)}">'
        'Return to your authored Core2A question (assisted review, not independent credit)'
        '</a></p>'
    )
    if 'data-g9-held-roundtrip=' in new_concept_article:
        raise AdaptationError('candidate already contains held adapter marker')
    new_concept_article = new_concept_article[:-len('</article>')] + return_link + '</article>'
    concept = concept.replace(concept_article, new_concept_article, 1)
    after = audit(package, manifest, pilot, practice, concept, package_ref=package_ref)
    if after['status'] != 'STRUCTURAL_CANDIDATE_HELD':
        raise AdaptationError('post-adaptation round-trip contract failed: '
                              + ','.join(after['errors']))
    return practice, concept, {
        'schema': 'imo-held-roundtrip-adapter/v1',
        'status': 'LOCAL_TEST_CANDIDATE_ADAPTED_NOT_PUBLISHED',
        'question_id': qid, 'microtopic_id': mic, 'step_id': step,
        'authorizes_learner_launch': False,
        'authorizes_independent_credit': False,
        'academic_qrt_approved': False,
        'browser_behavior_verified': False,
        'source_approved': False,
        'errors': [],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ('package', 'manifest', 'pilot', 'core2a', 'core1a'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    try:
        root = args.repo_root.resolve(strict=True)
        package_ref = args.package.resolve(strict=True).relative_to(root).as_posix()
        inputs = [json.loads(getattr(args, n).read_text(encoding='utf-8'))
                  for n in ('package', 'manifest', 'pilot')]
        core2a, core1a = (args.core2a.resolve(strict=True), args.core1a.resolve(strict=True))
        output = args.output_dir.resolve()
        if core2a.parent != core1a.parent or core2a.name != 'core2a.html' or core1a.name != 'core1a.html':
            raise AdaptationError('core2a/core1a pages must belong to same draft product')
        if output == core2a.parent or output.is_relative_to(core2a.parent):
            raise AdaptationError('never overwrite the original draft product')
        forbidden = tuple(root / x for x in ('public', 'docs', 'Mathematics', 'Releases', 'TEST'))
        if any(output == x or output.is_relative_to(x) for x in forbidden):
            raise AdaptationError('cannot stage adapted candidate under protected source or site trees')
        a,b,report = adapt(*inputs, core2a.read_text(encoding='utf-8'),
                           core1a.read_text(encoding='utf-8'), package_ref=package_ref)
        # Refuse to overwrite existing artifacts or partially approved outputs.
        if output.exists():
            raise AdaptationError('output directory already exists')
        output.mkdir(parents=True, exist_ok=False)
        (output / 'core2a.html').write_text(a, encoding='utf-8')
        (output / 'core1a.html').write_text(b, encoding='utf-8')
        (output / 'local-held-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        report = {'schema': 'imo-held-roundtrip-adapter/v1',
                  'status': 'HELD_NO_OUTPUT', 'authorizes_learner_launch': False,
                  'errors': [type(exc).__name__ + ': ' + str(exc)]}
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
