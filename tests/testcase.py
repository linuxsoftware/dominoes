#---------------------------------------------------------------------------
# Testing infrastructure
#---------------------------------------------------------------------------
import unittest

class TestCase(unittest.TestCase):
    """Adds extra assert methods"""
    # The unittest.TestCase asserts are:
    #   assertEqual(a, b)           a == b   
    #   assertNotEqual(a, b)        a != b   
    #   assertTrue(x)               bool(x) is True  
    #   assertFalse(x)              bool(x) is False         
    #   assertIs(a, b)              a is b
    #   assertIsNot(a, b)           a is not b
    #   assertIsNone(x)             x is None
    #   assertNotIn(a, b)           a not in b
    #   assertIsInstance(a, b)      isinstance(a, b)
    #   assertNotIsInstance(a, b)   not isinstance(a, b)
    #
    #   assertRaises(exc, fun, *args, **kwds)           raises exc
    #   assertRaisesRegex(exc, r, fun, *args, **kwds)   raises exc, matches r
    #   assertWarns(warn, fun, *args, **kwds)           raises warn
    #   assertWarnsRegex(warn, r, fun, *args, **kwds)   raises warn, matches r
    #   assertLogs(logger, level)                       logs to logger at level
    #
    #   assertAlmostEqual(a, b)     round(a-b, 7) == 0
    #   assertNotAlmostEqual(a, b)  round(a-b, 7) != 0
    #   assertGreater(a, b)         a > b
    #   assertGreaterEqual(a, b)    a >= b
    #   assertLess(a, b)            a < b
    #   assertLessEqual(a, b)       a <= b
    #   assertRegex(s, r)           r.search(s)
    #   assertNotRegex(s, r)        not r.search(s)
    #   assertCountEqual(a, b)      contents a == contents b ignoring order
    #
    #   assertMultiLineEqual(a, b)  compares strings
    #   assertSequenceEqual(a, b)   compares sequences
    #   assertListEqual(a, b)       compares lists
    #   assertTupleEqual(a, b)      compares tuples
    #   assertSetEqual(a, b)        compares sets or frozensets
    #   assertDictEqual(a, b)       compares dicts

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr),
                        'expected object %r to have attribute %r' % (obj, attr))

    def assertNoAttr(self, obj, attr):
        self.assertFalse(hasattr(obj, attr),
                         'object %r should not have attribute %r' % (obj, attr))

    # obsoleted by assertAlmostEqual, but different
    def assertNearlyEqual(self, a, b, tolerance):
        self.assertTrue(b-tolerance < a < b+tolerance,
                        '%r != %r \N{plus-minus sign} %r' % (a, b, tolerance))



