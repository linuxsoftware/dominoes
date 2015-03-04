#---------------------------------------------------------------------------
# Utility class tests
#---------------------------------------------------------------------------

from string import hexdigits
from pyramid.testing import DummyResource
from .helpers import UnitTestCase
import time
from io import BytesIO
from PIL import Image # pillow actually
from davezdominoes.gamecoordinator.utils import gauth

#---------------------------------------------------------------------------
class GAuthTests(UnitTestCase):
    def test_genKey(self):
        keys = set()
        for i in range(1000):
            hexKey = gauth.genKey()
            self.assertEqual(20, len(hexKey))
            self.assertTrue(all(digit in hexdigits for digit in hexKey))
            self.assertFalse(hexKey in keys)
            keys.add(hexKey)
        self.assertEqual(1000, len(keys))

    def test_getSecret(self):
        gauthKey  = "0102030405060708090a"
        userId    = 0
        secret = gauth.getSecret(gauthKey, userId)
        self.assertEqual(32, len(secret))
        self.assertEqual("5RZMT6HX25CFFEYCTRMC3TIWTGH7MLTJ", secret)

    def test_getUri(self):
        secret    = "KWYBE3DKQIT7NC74DSHMC7EEFZLUF2WH"
        loginName = "dummy"
        uri = gauth.getUri(secret, loginName)
        self.assertEqual("otpauth://totp/DavezDominoes:{loginName}"
                         "?secret={secret}&issuer=DavezDominoes"
                         .format(**locals()), uri)

    def test_getQRCode(self):
        gauthKey  = "0102030405060708090a"
        user = DummyResource(id    = 0,
                             login = "dummy")
        data = gauth.getQRCode(gauthKey, user)
        img = Image.open(BytesIO(data))
        self.assertEqual("PNG", img.format)
        self.assertEqual((294, 294), img.size)
        #img.show()
        #with open("testqr.png", "wb") as fout:
        #    fout.write(data)

    def test_verifyOneTimePassword(self):
        userId   = 0
        gauthkey = "0102030405060708090a"
        secret   = gauth.getSecret(gauthkey, userId)

        #monkeypatch time
        realTime = time.time
        time.time = lambda:1400000000
        self.assertTrue(gauth.verifyOneTimePassword("236108", secret))
        time.time = realTime

#---------------------------------------------------------------------------
