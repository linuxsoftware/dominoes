#---------------------------------------------------------------------------
# Utility class tests
#---------------------------------------------------------------------------

from ..testcase import TestCase

#---------------------------------------------------------------------------
class StringTests(TestCase):
    def test_addUrlQueryParams(self):
        from davezdominoes.commoncode.utils import addUrlQueryParams
        url = "https://70s.music/find?name=olivia&name=newton&song=magic"
        url = addUrlQueryParams(url, name="john", song="xanadu")
        self.assertTrue(url, "https://70s.music/find?name=olivia&name=newton"
                        "&song=magic&name=john&song=xanadu")


#---------------------------------------------------------------------------
