import unittest
from nexusvi_test_summary import summarize

OK = 'test result: ok. 5 passed; 0 failed; 2 ignored; 0 measured; 3 filtered out; finished in 0.12s'
FAIL = 'test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.02s'


class TestSummary(unittest.TestCase):
    def test_multiple_binaries(self):
        r = summarize(OK + '\n' + OK, 0)
        self.assertEqual(r['test_groups'], 2)
        self.assertEqual(r['cargo_totals'], dict(passed=10, failed=0, ignored=4, measured=0, filtered=6))
        self.assertEqual(r['status'], 'reported_pass')

    def test_failed_group(self):
        self.assertEqual(summarize(OK + '\n' + FAIL, 0)['status'], 'failed')

    def test_nonzero_exit(self):
        self.assertEqual(summarize(OK, 101)['status'], 'failed')

    def test_no_results(self):
        self.assertEqual(summarize('Compiling xcl', 0)['status'], 'incomplete')

    def test_empty_suite(self):
        self.assertEqual(summarize(OK.replace('5 passed', '0 passed'), 0)['status'], 'incomplete')

    def test_skips_are_not_gpu_coverage(self):
        r = summarize(OK + '\nSKIPPED a: no GPU\nSKIPPED b: no GPU', 0)
        self.assertEqual(r['observed_skip_events'], {'no GPU': 2})
        self.assertEqual(r['cargo_totals']['passed'], 5)
        self.assertEqual(r['hardware_coverage'], 'not established by this log summary')

    def test_ansi_and_crlf(self):
        r = summarize('\x1b[32m' + OK + '\x1b[0m\r\n', 0)
        self.assertEqual(r['status'], 'reported_pass')


    def test_truncated_last_suite(self):
        r = summarize('running 7 tests\n' + OK + '\nrunning 1 test', 0)
        self.assertEqual(r['status'], 'incomplete')
        self.assertTrue(r['suite_integrity']['unfinished_suite'])

    def test_mismatched_suite_size(self):
        r = summarize('running 8 tests\n' + OK, 0)
        self.assertEqual(r['status'], 'incomplete')
        self.assertEqual(r['suite_integrity']['mismatches'], 1)

    def test_complete_timestamped_log(self):
        stamp = '2026-11-27T09:19:21.0055939Z '
        log = '\n'.join(stamp + x for x in ['running 7 tests', OK])
        r = summarize(log, 0, 'abc')
        self.assertEqual(r['status'], 'reported_pass')
        self.assertEqual(r['revision'], 'abc')
        self.assertEqual(r['suite_integrity']['starts'], 1)

    def test_skip_events_distinct_from_names_and_missing_samples(self):
        r = summarize(OK + '\nSKIPPED a: no GPU\nSKIPPED a: no GPU\n'
                      'SKIPPED b: no GPU\nnot set, their tests are skipped: XCL_SAMPLE_A, XCL_SAMPLE_B', 0)
        self.assertEqual(r['distinct_observed_skip_names'], 2)
        self.assertEqual(r['observed_skip_events'], {'no GPU': 3})
        self.assertEqual(r['missing_sample_variables'], ['XCL_SAMPLE_A', 'XCL_SAMPLE_B'])

    def test_failed_name(self):
        r = summarize('running 3 tests\ntest module::bad ... FAILED\n' + FAIL, 1)
        self.assertEqual(r['failed_test_names'], ['module::bad'])
        self.assertEqual(r['status'], 'failed')

    def test_unmatched_summary_with_starts(self):
        self.assertEqual(summarize('running 7 tests\n' + OK + '\n' + OK, 0)['status'], 'incomplete')


if __name__ == '__main__':
    unittest.main()
