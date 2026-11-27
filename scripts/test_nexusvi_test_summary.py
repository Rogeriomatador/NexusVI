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


if __name__ == '__main__':
    unittest.main()
