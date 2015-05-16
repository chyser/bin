#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from Crypto.Cipher import AES
from Crypto import Random

from pbkdf2 import PBKDF2

import pylib.osscripts as oss
import pylib.util as util
import pickle
import zlib


class EncrpytedStorageException(Exception): pass

#-------------------------------------------------------------------------------
class EncrpytedStorageString(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, fileName, passwd, padValue='\0'):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.fileName = fileName
        self.padValue = padValue
        self.passwd = passwd

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        with open(self.fileName, 'rb') as inf:
            pwSalt = inf.read(8)
            iv = inf.read(AES.block_size)
            ctxt = inf.read()

        key = getKey(self.passwd, 32, pwSalt)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        try:
            return zlib.decompress(cipher.decrypt(ctxt))[3:].rstrip(self.padValue)
        except zlib.error as err:
            raise EncrpytedStorageException('\n\nCannot Decrypt File\n\n' + str(err))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self, ptxt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mkBackup()

        iv = Random.new().read(AES.block_size)
        salt = mkSalt(3)

        pwSalt = mkSalt(8)
        key = getKey(self.passwd, 32, pwSalt)

        ptxt = pad(zlib.compress(salt + ptxt.encode('utf-8'), 9), AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ctxt = cipher.encrypt(ptxt)

        with open(self.fileName, 'wb') as otf:
            otf.write(pwSalt)
            otf.write(iv)
            otf.write(ctxt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mkBackup(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        util.mkBackups(self.fileName, 5)
        oss.mv(self.fileName, self.fileName + '.bak')


#-------------------------------------------------------------------------------
class EncryptedStorageObj(EncrpytedStorageString):
#-------------------------------------------------------------------------------
    """ An encrypted pickle of arbitrary python objs saved into storage
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def load(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return pickle.loads(EncrpytedStorageString.load(self))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def save(self, obj):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return EncrpytedStorageString.save(self, pickle.dumps(obj))


#-------------------------------------------------------------------------------
def pad(txt, length, padValue='\0', maxLength=None):
#-------------------------------------------------------------------------------
    """ pad txt to a certain 'length' using the specified 'padValue' and truncating
        to a maximum length 'maxLength' if specified.
    """
    pl = len(txt) % length
    if pl:
        pl = length - pl

    pv = padValue.encode('utf-8')
    if len(pv) != 1:
        raise EncrpytedStorageException('padValue must be 1 byte in length')

    if maxLength:
        return (txt + (pv * pl))[:maxLength]
    return txt + (pv * pl)


#-------------------------------------------------------------------------------
def mkSalt(length):
#-------------------------------------------------------------------------------
    """ make an ascii salt value of the specified 'length'
    """
    return Random.new().read(length)


#-------------------------------------------------------------------------------
def getKey(passwd, length, salt=None):
#-------------------------------------------------------------------------------
    if salt is None:
        salt = mkSalt(8)
    return PBKDF2(passwd, salt).read(length)

#-------------------------------------------------------------------------------
def __test__(verbose=False):
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    #import pylib.tester as tester

    es = EncryptedStorageObj('/tmp/es.enc', b'coolstuff')


    d = {'cool' : 'aidan', 'boo' : 'sara'}
    es.save(d)

    dd = es.load()
    print(dd)

    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__(verbose=True)
    oss.exit(res)

