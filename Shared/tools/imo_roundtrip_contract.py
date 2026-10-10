#!/usr/bin/env python3
"""Non-publishing IMO Core2A -> Core1A -> Core2A HTML round-trip audit.

This read-only pre-release *structural* contract cannot prove browser behavior,
independent mastery, academic/QRT acceptance, rights, or release eligibility.
It deliberately fails on missing or ambiguous exact-step/return navigation.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from Shared.tools.imo_handoff_preflight import check as check_candidate  # noqa: E402


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.articles: list[dict] = []
        self.current: dict | None = None
        self.article_depth = 0
        self.template_stack: list[str | None] = []
        self.ids: list[str] = []
        self.duplicate_attributes: list[str] = []
        self.base_tags = 0

    def handle_starttag(self, tag: str, pairs: list[tuple[str, str | None]]) -> None:
        attrs = dict(pairs)
        keys = [name for name, _ in pairs]
        if len(keys) != len(set(keys)):
            self.duplicate_attributes.append(tag)
        if tag == 'base':
            self.base_tags += 1
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'article':
            if self.current is None:
                self.current = {'attrs': attrs, 'links': [], 'steps': [],
                                'templates': [], 'gated': []}
                self.articles.append(self.current)
                self.article_depth = 1
            else:
                self.article_depth += 1
        if tag == 'template':
            self.template_stack.append(attrs.get('data-g9-payload'))
        if self.current is None:
            return
        if tag == 'a':
            self.current['links'].append({'attrs': attrs, 'template': self.template_stack[-1]
                                          if self.template_stack else None})
        if tag == 'li' and attrs.get('data-g9-step'):
            self.current['steps'].append(attrs)
        if tag == 'template' and attrs.get('data-g9-payload'):
            self.current['templates'].append(attrs['data-g9-payload'])
        if tag == 'details' and 'data-requires-attempt' in attrs:
            self.current['gated'].append(attrs.get('data-g9-payload-ref'))

    def handle_endtag(self, tag: str) -> None:
        if tag == 'template' and self.template_stack:
            self.template_stack.pop()
        if tag == 'article' and self.current is not None:
            self.article_depth -= 1
            if self.article_depth == 0:
                self.current = None


def audit(package: dict, manifest: dict, pilot: dict, core2a_html: str,
          core1a_html: str, *, package_ref: str | None = None) -> dict:
    preflight = check_candidate(package, manifest, pilot, package_ref=package_ref)
    errors = list(preflight['errors'])

    def need(value: bool, code: str) -> None:
        if not value:
            errors.append(code)

    qid, mic, step = (preflight.get(k) for k in ('question_id', 'microtopic_id', 'repair_step_id'))
    a, b = Page(), Page()
    try:
        a.feed(core2a_html)
        a.close()
        b.feed(core1a_html)
        b.close()
    except (ValueError, TypeError):
        errors.append('INVALID_HTML_INPUT')
    need(not a.duplicate_attributes and not b.duplicate_attributes, 'DUPLICATE_HTML_ATTRIBUTES')
    need(a.base_tags == 0 and b.base_tags == 0, 'BASE_URL_OVERRIDE_FORBIDDEN')
    need(len(a.ids) == len(set(a.ids)), 'CORE2A_DUPLICATE_DOM_IDS')
    need(len(b.ids) == len(set(b.ids)), 'CORE1A_DUPLICATE_DOM_IDS')

    qarticles = [x for x in a.articles if x['attrs'].get('id') == qid
                 and x['attrs'].get('data-g9-role') == 'CORE2A']
    concepts = [x for x in b.articles if x['attrs'].get('id') == mic
                and x['attrs'].get('data-g9-role') == 'CORE1A']
    need(len(qarticles) == 1, 'CORE2A_EXACT_QUESTION_ARTICLE_MISSING')
    need(len(concepts) == 1, 'CORE1A_EXACT_CONCEPT_ARTICLE_MISSING')
    if qarticles:
        q = qarticles[0]
        protected = f'CORE2A-{qid}-reasoning'
        need(q['templates'].count(protected) == 1, 'CORE2A_REASONING_TEMPLATE_MISSING')
        need(q['gated'].count(protected) == 1, 'CORE2A_POST_ATTEMPT_GATE_MISSING')
        repair = [link for link in q['links'] if 'data-g9-repair-ref' in link['attrs']]
        need(len(repair) == 1, 'CORE2A_EXACT_REPAIR_LINK_MISSING')
        if repair:
            link = repair[0]
            attrs = link['attrs']
            need(link['template'] == protected, 'REPAIR_LEAKS_BEFORE_ATTEMPT')
            need(attrs.get('data-g9-repair-ref') == step, 'REPAIR_STEP_REF_MISMATCH')
            need(attrs.get('data-g9-concept-ref') == mic, 'REPAIR_CONCEPT_REF_MISMATCH')
            need(attrs.get('data-g9-repair-target') == step, 'REPAIR_TARGET_NOT_EXACT_STEP')
            need(attrs.get('href') == f'core1a.html#{step}', 'REPAIR_HREF_NOT_EXACT_STEP')
    if concepts:
        concept = concepts[0]
        steps = [x for x in concept['steps'] if x.get('data-g9-step') == step]
        need(len(steps) == 1, 'CORE1A_TEACHING_STEP_NOT_FOUND')
        if steps:
            need(steps[0].get('id') == step, 'CORE1A_STEP_NOT_ADDRESSABLE')
        returns = [x for x in concept['links'] if 'data-g9-practice-link' in x['attrs']]
        matching = [x for x in returns if x['attrs'].get('data-g9-question-ref') == qid]
        need(len(matching) == 1, 'CORE1A_EXACT_CORE2A_RETURN_MISSING')
        if matching:
            target = matching[0]['attrs']
            need(target.get('data-g9-concept-ref') == mic, 'RETURN_CONCEPT_REF_MISMATCH')
            need(target.get('href') == f'core2a.html#{qid}', 'RETURN_HREF_NOT_CORE2A')
    return {
        'schema': 'imo-f04-held-roundtrip-structure/v1',
        'status': 'STRUCTURAL_CANDIDATE_HELD' if not errors else 'ROUNDTRIP_GAPS_HELD',
        'question_id': qid, 'microtopic_id': mic, 'repair_step_id': step,
        'authorizes_learner_launch': False,
        'authorizes_independent_credit': False,
        'browser_behavior_verified': False,
        'academic_qrt_source_approved': False,
        'errors': sorted(set(errors)),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for arg in ('package', 'manifest', 'pilot', 'core2a', 'core1a'):
        p.add_argument('--' + arg, type=Path, required=True)
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    try:
        inputs = [json.loads(getattr(args, name).read_text(encoding='utf-8'))
                  for name in ('package', 'manifest', 'pilot')]
        package_ref = args.package.resolve(strict=True).relative_to(
            args.repo_root.resolve(strict=True)).as_posix()
        a_file = args.core2a.resolve(strict=True)
        b_file = args.core1a.resolve(strict=True)
        if (a_file.name != 'core2a.html' or b_file.name != 'core1a.html'
                or a_file.parent != b_file.parent):
            raise ValueError('Core2A and Core1A must be role pages in one candidate product directory')
        h1 = a_file.read_text(encoding='utf-8')
        h2 = b_file.read_text(encoding='utf-8')
        result = audit(*inputs, h1, h2, package_ref=package_ref)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'schema': 'imo-f04-held-roundtrip-structure/v1',
                  'status': 'ROUNDTRIP_GAPS_HELD',
                  'authorizes_learner_launch': False,
                  'authorizes_independent_credit': False,
                  'browser_behavior_verified': False,
                  'academic_qrt_source_approved': False,
                  'errors': ['INPUT_OR_PATH_' + type(exc).__name__]}
    out = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding='utf-8')
    print(out, end='')
    return 0 if result['status'] == 'STRUCTURAL_CANDIDATE_HELD' else 1


if __name__ == '__main__':
    raise SystemExit(main())
