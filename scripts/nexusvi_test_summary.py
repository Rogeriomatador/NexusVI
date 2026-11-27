"""Summarize Cargo test logs without claiming hardware coverage (GPL-2.0-only)."""
import argparse
import json
import re
from pathlib import Path

RESULT = re.compile(
    r'^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; '
    r'(\d+) ignored; (\d+) measured; (\d+) filtered out(?:;.*)?$'
)
SKIP = re.compile(r'^SKIPPED\s+(\S+):\s*(.+)$')
START = re.compile(r'^running (\d+) tests?$')
FAILED = re.compile(r'^test (.+) \.\.\. FAILED$')
MISSING = re.compile(r'^not set, their tests are skipped: (.+)$')
STAMP = re.compile(r'^\d{4}-\d\d-\d\dT\S+Z ')
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def summarize(log, exit_code, revision=None):
    totals = dict(passed=0, failed=0, ignored=0, measured=0, filtered=0)
    groups = 0
    failed_groups = 0
    skips = {}
    skip_tests = set()
    failures = set()
    missing = set()
    starts = 0
    pending = None
    mismatches = 0
    unmatched = 0
    for raw in log.splitlines():
        line = STAMP.sub('', ANSI.sub('', raw)).strip()
        start = START.fullmatch(line)
        if start:
            starts += 1
            if pending is not None:
                mismatches += 1
            pending = int(start[1])
        failed = FAILED.fullmatch(line)
        if failed:
            failures.add(failed[1])
        unavailable = MISSING.fullmatch(line)
        if unavailable:
            missing.update(x.strip() for x in unavailable[1].split(','))
        result = RESULT.fullmatch(line)
        if result:
            groups += 1
            failed_groups += result[1] == 'FAILED'
            counts = [int(value) for value in result.groups()[1:]]
            for key, value in zip(totals, counts):
                totals[key] += value
            if pending is None:
                unmatched += 1
            elif pending != sum(counts[:4]):
                mismatches += 1
            pending = None
        skip = SKIP.fullmatch(line)
        if skip:
            name, reason = skip.groups()
            skip_tests.add(name)
            skips[reason] = skips.get(reason, 0) + 1
    incomplete = bool(pending is not None or mismatches or (starts and unmatched))
    # A successful exit without test summaries is not a valid test report.
    # Cargo's "passed" count can include tests that returned early on missing GPUs.
    return {
        'schema_version': 2,
        'revision': revision,
        'exit_code': exit_code,
        'status': ('failed' if exit_code != 0 or failed_groups or totals['failed']
                   else 'reported_pass' if groups and totals['passed'] and not incomplete else 'incomplete'),
        'test_groups': groups,
        'suite_integrity': {
            'starts': starts,
            'unmatched_summaries': unmatched,
            'mismatches': mismatches,
            'unfinished_suite': pending is not None,
            'start_markers_available': bool(starts),
        },
        'failed_test_names': sorted(failures),
        'missing_sample_variables': sorted(missing),
        'distinct_observed_skip_names': len(skip_tests),
        'cargo_totals': totals,
        'observed_skip_events': dict(sorted(skips.items())),
        'hardware_coverage': 'not established by this log summary',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--exit-code', type=int, required=True)
    parser.add_argument('--revision', help='Exact Git commit tested')
    args = parser.parse_args()
    raw = args.log.read_bytes()
    # Windows PowerShell 5.1 redirection commonly writes UTF-16 with a BOM.
    encoding = 'utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
    report = summarize(raw.decode(encoding), args.exit_code, args.revision)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report['status'] == 'reported_pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
