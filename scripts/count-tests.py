"""Run one unittest module and print "<passed> <total>" (used by run-evals.sh for hidden tests)."""
import os
import sys
import unittest

# Python puts this script's folder on the import path, not the folder it runs in.
sys.path.insert(0, os.getcwd())

suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[1])
result = unittest.TestResult()
suite.run(result)
# A test with several failing subtests is listed once per subtest; count it once.
failed = {id(getattr(test, "test_case", test)) for test, _ in result.failures + result.errors}
print(result.testsRun - len(failed), result.testsRun)
