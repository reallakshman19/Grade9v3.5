#!/usr/bin/env python3
"""Native-only Q003 vs G-CORE2-R2 structural benchmark; zero source-text publication."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = HERE / '.private'
GOLDEN = ROOT / 'golden/units/G-CORE2-R2/rendered'


class Markers(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = {}
        self.tags = Counter()
        self.components = Counter()
        self.blocks = Counter()

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        d = dict(attrs)
        if 'data-g9-component' in d:
            self.components[d['data-g9-component']] += 1
        if 'data-g9-block' in d:
            self.blocks[d['data-g9-block']] += 1
        for attr in ('data-g9-role', 'data-g9-commit', 'data-g9-response-type',
                     'data-g9-attempt-box', 'data-g9-ladder', 'data-g9-protected'):
            if attr in d:
                self.attrs.setdefault(attr, Counter())[d[attr] or 'PRESENT'] += 1


def snapshot(path: Path) -> dict:
    html = path.read_text(encoding='utf-8')
    p = Markers()
    p.feed(html)
    return {
        'sha256': sha256(path.read_bytes()).hexdigest(),
        'bytes': path.stat().st_size,
        'registered_blueprint_marker': 'BP-CORE2-SOURCE-QUESTION' in html,
        'core2_role': p.attrs.get('data-g9-role', {}).get('CORE2', 0) > 0,
        'typed_single_choice': p.attrs.get('data-g9-response-type', {}).get('single_choice', 0) > 0,
        'typed_commit_count': sum(p.attrs.get('data-g9-commit', {}).values()),
        'attempt_box_count': sum(p.attrs.get('data-g9-attempt-box', {}).values()),
        'ladder_count': sum(p.attrs.get('data-g9-ladder', {}).values()),
        'components': sorted(p.components),
        'blocks': sorted(p.blocks),
    }


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-input', required=True, type=Path)
    parser.add_argument('--custody-receipt', type=Path)
    args = parser.parse_args()
    if not (ROOT / 'Shared/tools/render_core.py').is_file():
        parser.error('BLOCKED: full native checkout with Shared/tools/render_core.py required')
    command = [sys.executable, '-I', str(HERE / 'prepare_private.py'),
               '--private-input', str(args.private_input.resolve())]
    if args.custody_receipt is not None:
        command += ['--custody-receipt', str(args.custody_receipt.resolve())]
    run(command)  # same adapter, never a second HTML composer
    run([sys.executable, '-I', str(ROOT / 'Shared/tools/build_golden.py'),
         '--id', 'G-CORE2-R2'])  # sole renderer, candidate golden
    q_html = STAGE / 'rendered/core2.html'
    g_html = GOLDEN / 'core2.html'
    q_receipt = json.loads((STAGE / 'rendered/render-receipt.json').read_text(encoding='utf-8'))
    g_receipt = json.loads((GOLDEN / 'render-receipt.json').read_text(encoding='utf-8'))
    q, g = snapshot(q_html), snapshot(g_html)
    required = {'IDENTITY', 'STEM', 'ATTEMPT', 'SOLUTION', 'SOLUTION_STEPS', 'ANSWER'}
    for label, page in (('Q003', q), ('G-CORE2-R2', g)):
        page['missing_required_components'] = sorted(required.difference(page['components']))
        page['native_structure_ok'] = (page['registered_blueprint_marker']
            and page['core2_role'] and page['typed_single_choice']
            and page['typed_commit_count'] >= 1
            and not page['missing_required_components'])
    gaps = {'Q003': len(q_receipt.get('gaps', [])), 'G-CORE2-R2': len(g_receipt.get('gaps', []))}
    report = {
        'issue': 183, 'task': '183-T3-G2-W1', 'aim': 'v3.1.0', 'outcome': 'O3',
        'source': 'NATIVE_ONLY: Shared/tools/render_core.py via prepare_private.py and build_golden.py',
        'golden_status': 'CANDIDATE_NOT_OWNER_BLESSED',
        'renderer_version': {'Q003': q_receipt.get('renderer'), 'G-CORE2-R2': g_receipt.get('renderer')},
        'renderer_digest': {'Q003': q_receipt.get('digest'), 'G-CORE2-R2': g_receipt.get('digest')},
        'gaps': gaps, 'pages': {'Q003': q, 'G-CORE2-R2': g},
        'golden_components_absent_from_Q003': sorted(set(g['components']) - set(q['components'])),
        'Q003_components_absent_from_golden': sorted(set(q['components']) - set(g['components'])),
        'scope': 'Native structural benchmark; NOT browser visual/pixel comparison or Owner QRT approval',
        'status': 'STRUCTURAL_CHECK_ONLY' if all(x['native_structure_ok'] for x in (q,g))
            and all(v == 0 for v in gaps.values()) else 'NATIVE_GAPS_OR_STRUCTURE_FINDINGS',
        'owner_qrt_accepted': False, 'same_page_a4': 'NOT_RUN', 'published': False,
    }
    STAGE.mkdir(parents=True, exist_ok=True)
    out = STAGE / 'native-golden-comparison.json'
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('NATIVE_GOLDEN_COMPARISON ' + report['status'])
    print('source-safe receipt: ' + str(out))
    return 0 if report['status'] == 'STRUCTURAL_CHECK_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
