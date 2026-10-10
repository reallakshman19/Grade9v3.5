#!/usr/bin/env python3
"""Read-only academic handoff identity preflight for an unadmitted IMO TEST candidate.

This checks that supported Core2A practice points at a real, uniquely identified
Core1A teaching step and remains TEST-only. It never generates a learner link,
accepts QRT, authenticates SOF sources, or overrides release_authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def check(package: dict, manifest: dict, pilot: dict, *, package_ref: str | None = None) -> dict:
    errors: list[str] = []
    def need(ok: bool, why: str) -> None:
        if not ok:
            errors.append(why)

    need(package.get('subject') == manifest.get('subject') == 'TEST', 'TEST_BOUNDARY')
    need(package.get('status') == 'CANDIDATE', 'UNADMITTED_PACKAGE_REQUIRED')
    extension = package.get('extensions') or {}
    need(all(extension.get(k) is False for k in (
        'grade9v3:qrt_admitted', 'grade9v3:core2_source_custody_granted',
        'grade9v3:learner_published')), 'PACKAGE_PUBLICATION_MUST_REMAIN_HELD')
    need(manifest.get('schema') == 'product-manifest/v1', 'MANIFEST_SCHEMA')
    need(manifest.get('output_roles') == ['CORE1A', 'CORE2A'], 'ROLE_BOUNDARY')
    selection = manifest.get('selection') or {}
    need(not selection.get('core2') and not selection.get('core2b'), 'SOURCE_CORE2_CANNOT_BE_SELECTED')
    need(not manifest.get('bank_refs'), 'NO_SOURCE_BANK_IN_CANDIDATE')
    scope = pilot.get('scope') or {}
    need(scope.get('subtopic_id') == 'NS-INDEX-LAWS', 'SUBTOPIC_ID')
    pilot_candidate = pilot.get('authored_teaching_candidate') or {}
    need(package.get('package_id') == pilot_candidate.get('package_id')
         and bool(package.get('package_id')), 'PACKAGE_RESEARCH_IDENTITY_MISMATCH')
    need(scope.get('launch_authorized') is False, 'NO_LAUNCH_AUTHORITY')
    need(scope.get('source_core2_admitted') == 0, 'SOURCE_CORE2_HELD')
    need(scope.get('learner_products_released') == 0, 'LEARNER_PRODUCT_HELD')
    routing = pilot.get('routing') or {}
    need(all(routing.get(k) is None for k in (
        'core1a_product_url', 'core2a_authored_product_url', 'core2_source_product_url')),
        'NO_LEARNER_PRODUCT_URL_WHILE_HELD')
    selected_mic = selection.get('microtopics') or []
    selected_q = selection.get('core2a') or []
    need(isinstance(selected_mic, list) and len(selected_mic) == 1
         and isinstance(selected_mic[0], str) and bool(selected_mic[0]),
         'ONE_UNIQUE_TEACHING_MICROTOPIC')
    need(isinstance(selected_q, list) and len(selected_q) == 1
         and isinstance(selected_q[0], str) and bool(selected_q[0]),
         'ONE_UNIQUE_AUTHORED_QUESTION')
    microtopics = [m for m in package.get('microtopics', []) if isinstance(m, dict)]
    questions = [q for q in package.get('questions', []) if isinstance(q, dict)]
    mic_by_id = {m.get('id'): m for m in microtopics}
    q_by_id = {q.get('id'): q for q in questions}
    need(len(microtopics) == len(mic_by_id), 'DUPLICATE_TEACHING_MICROTOPIC_ID')
    need(len(questions) == len(q_by_id), 'DUPLICATE_AUTHORED_QUESTION_ID')
    selected_steps: list[str] = []
    repair_ref = None
    question_id = selected_q[0] if len(selected_q) == 1 and isinstance(selected_q[0], str) else None
    microtopic_id = selected_mic[0] if len(selected_mic) == 1 and isinstance(selected_mic[0], str) else None
    need(microtopic_id == pilot_candidate.get('microtopic_id') and bool(microtopic_id),
         'MICROTOPIC_RESEARCH_IDENTITY_MISMATCH')
    concept = mic_by_id.get(microtopic_id)
    question = q_by_id.get(question_id)
    need(concept is not None, 'MICROTOPIC_NOT_RESOLVED')
    need(question is not None, 'QUESTION_NOT_RESOLVED')
    if concept:
        need(concept.get('status') == 'CANDIDATE', 'MICROTOPIC_NOT_CANDIDATE')
        need(concept.get('primary_capability_ref') == pilot_candidate.get('capability_id'),
             'CAPABILITY_RESEARCH_IDENTITY_MISMATCH')
        selected_steps = [s.get('id') for s in concept.get('teaching_path', []) if isinstance(s, dict)]
        need(bool(selected_steps) and all(isinstance(s, str) and s for s in selected_steps)
             and len(selected_steps) == len(set(selected_steps)), 'TEACHING_STEPS_NOT_UNIQUE')
    if question:
        repair_ref = question.get('repair_ref')
        need(question.get('origin') == 'AUTHORED' and question.get('status') == 'CANDIDATE',
             'SUPPORTED_PRACTICE_MUST_BE_AUTHORED_CANDIDATE')
        need(any(isinstance(e, dict) and e.get('core') == 'CORE2A' for e in question.get('exposure', [])),
             'CORE2A_EXPOSURE_REQUIRED')
        need(all(e.get('core') != 'CORE2' for e in question.get('exposure', []) if isinstance(e, dict)),
             'SOURCE_CORE2_EXPOSURE_FORBIDDEN')
        need(bool(repair_ref) and repair_ref in selected_steps, 'REPAIR_STEP_UNRESOLVED')
    if concept and question:
        capability_id = concept.get('primary_capability_ref')
        need(question.get('primary_capability_ref') == capability_id, 'CAPABILITY_MISMATCH')
        caps = [c for c in package.get('capabilities', []) if isinstance(c, dict)
                and c.get('id') == capability_id and c.get('status') == 'CANDIDATE']
        need(len(caps) == 1, 'CAPABILITY_RECORD_NOT_RESOLVED')
        routes = [r for r in package.get('teaching_routes', []) if isinstance(r, dict)
                  and r.get('status') == 'CANDIDATE'
                  and r.get('microtopic_refs') == [microtopic_id]
                  and 'CORE1A' in r.get('cores', [])]
        need(len(routes) == 1, 'CORE1A_TEACHING_ROUTE_NOT_RESOLVED')
    refs = manifest.get('package_refs')
    need(isinstance(refs, list) and len(refs) == 1
         and isinstance(refs[0], str)
         and refs[0].startswith('TEST/imo-research/candidates/')
         and '..' not in refs[0].split('/') and refs[0].endswith('.json'),
         'EXACT_ONE_PACKAGE_REF_REQUIRED')
    if package_ref is not None:
        need(isinstance(refs, list) and len(refs) == 1 and refs[0] == package_ref,
             'MANIFEST_PACKAGE_REF_MISMATCH')
    return {
        'schema': 'imo-f04-unadmitted-handoff-preflight/v1',
        'state': 'CANDIDATE_HELD_WELL_FORMED' if not errors else 'INCONSISTENT_CANDIDATE_HOLD',
        'authorizes_learner_launch': False,
        'authorizes_academic_qrt_or_source': False,
        'microtopic_id': microtopic_id,
        'question_id': question_id,
        'repair_step_id': repair_ref,
        'errors': errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        obj = [json.loads(p.read_text(encoding='utf-8')) for p in (args.package, args.manifest, args.pilot)]
        root = args.repo_root.resolve(strict=True)
        package_path = args.package.resolve(strict=True)
        relative = package_path.relative_to(root).as_posix()
        result = check(*obj, package_ref=relative)
    except (OSError, ValueError, TypeError) as exc:
        result = {'schema': 'imo-f04-unadmitted-handoff-preflight/v1',
                  'state': 'INCONSISTENT_CANDIDATE_HOLD', 'authorizes_learner_launch': False,
                  'authorizes_academic_qrt_or_source': False,
                  'errors': [f'INPUT_UNREADABLE_{type(exc).__name__}']}
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0 if result['state'] == 'CANDIDATE_HELD_WELL_FORMED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
