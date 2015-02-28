#!/usr/bin/env python
"""
"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import osscripts as oss
import sys

if sys.platform == 'win32':
    PRGM = '"C:/Program Files/Apache Software Foundation/Apache2.2/bin/openssl.exe" '
    if not oss.exists('openssl.cnf'):
        oss.cp('C:/Program Files/Apache Software Foundation/Apache2.2/conf/openssl.cnf', '.')
    CNF = ' -config openssl.cnf'
else:
    PRGM = 'openssl'
    CNF = ''



ROOT_SUBJECT = "/C=US/ST=NewYork/O=HP_LABS_SIEL_SDC_CA"
SUBJECT = "/C=US/ST=NewYork/O=HP_LABS_SIEL_SDC"
DAYS = 365


#-------------------------------------------------------------------------------
def catFile(infn, otfn, append=False):
#-------------------------------------------------------------------------------
    inf = open(infn)
    buf = inf.read()

    otf = open(otfn, 'a' if append else 'w')
    otf.write(buf)
    inf.close()
    otf.close()


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:

        -g | --genKey      : generate 2048 bit RSA private/public key pair in pem format to arg[0]
        -r | --genRootCert : generate a self-signed root certificate using key (-k) into arg[0]
        -c | --genCert     : generate a certificate (key/cert) signed by root CA (-R/-k) into arg[0]
        -k | --key         : specifies key to use
        -R | --rootCert    : specifies CA cert to use
    """
    args, opts = oss.gopt(argv[1:], [('r', 'genRootCert'), ('g', 'genKey'), ('c', 'genCert')], [('k', 'key'), ('R', 'rootCert')], __doc__ + main.__doc__)


    if opts.genKey:
        oss.r(PRGM + 'genrsa 2048 > %s' % args[0])
        oss.exit()

    if opts.genRootCert:
        oss.r(PRGM + 'req -x509 -new -days %d -key %s %s -subj %s > %s' % (DAYS, opts.key, CNF, ROOT_SUBJECT, args[0]))

    elif opts.genCert:
        kf = 'openssl_kf_tmp.pem'
        cs = 'openssl_cf_tmp.csr'
        cf = 'openssl_cf_tmp.crt'

        oss.r(PRGM + 'genrsa 2048 > %s' % kf)
        oss.r(PRGM + 'req -new -days %d -key %s %s -subj %s> %s' % (DAYS, kf, CNF, SUBJECT, cs))
        oss.r(PRGM + 'x509 -req -in %s -CA %s -CAkey %s -CAcreateserial > %s' % (cs, opts.rootCert, opts.key, cf))

        catFile(kf, args[0])
        catFile(cf, args[0], append=True)

    if len(args) > 0:
        oss.r(PRGM + ' x509 -text < %s' % args[0])

    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)

