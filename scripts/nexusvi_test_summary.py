"""Summarize Cargo test logs without claiming hardware coverage (GPL-2.0-only)."""
import argparse
import json
import re
from pathlib import Path

RESULT = re.compile(
    r'^test result: (ok|FAILED)\. (\d+) passed; (\d+) failed; '
    r'(\d+) ignored; (\d+) measured; (\d+) filtered out(?:;.*)?$'
)
SKIP = re.compile(r'^SKIPPED\s+\S+:\s*(.+)$')
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


def summarize(log, exit_code):
    totals = dict(passed=0, failed=0, ignored=0, measured=0, filtered=0)
    groups = 0
    failed_groups = 0
    skips = {}
    for raw in log.splitlines():
        line = ANSI.sub('', raw).strip()
        result = RESULT.fullmatch(line)
        if result:
            groups += 1
            failed_groups += result[1] == 'FAILED'
            for key, value in zip(totals, result.groups()[1:]):
                totals[key] += int(value)
        skip = SKIP.fullmatch(line)
        if skip:
            reason = skip[1]
            skips[reason] = skips.get(reason, 0) + 1
    # A successful exit without test summaries is not a valid test report.
    # Cargo's "passed" count can include tests that returned early on missing GPUs.
    return {
        'schema_version': 1,
        'exit_code': exit_code,
        'status': ('failed' if exit_code != 0 or failed_groups or totals['failed']
                   else 'reported_pass' if groups and totals['passed'] else 'incomplete'),
        'test_groups': groups,
        'cargo_totals': totals,
        'observed_skip_events': dict(sorted(skips.items())),
        'hardware_coverage': 'not established by this log summary',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--exit-code', type=int, required=True)
    args = parser.parse_args()
    raw = args.log.read_bytes()
    # Windows PowerShell 5.1 redirection commonly writes UTF-16 with a BOM.
    encoding = 'utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
    report = summarize(raw.decode(encoding), args.exit_code)
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report['status'] == 'reported_pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
