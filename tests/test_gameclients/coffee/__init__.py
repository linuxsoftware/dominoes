#---------------------------------------------------------------------------
# Test Coffee code
#---------------------------------------------------------------------------

from .suite import QUnitSuite

def load_tests(loader, tests, pattern):
    tests.addTest(QUnitSuite("test_gameclient.html"))
    return tests
