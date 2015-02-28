#!/usr/bin/env python
"""
usage: testwbem.py [options] <host_name>

options:
    -u | --user   : specify user name
    -p | --passwd : specify passwd

"""

import pywbem

import pylib.osscripts as oss

#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage:
    """
    args, opts = oss.gopt(argv[1:], [], [('u', 'user'), ('p', 'passwd')], __doc__ + main.__doc__)

    if len(args) < 1:
        oss._usage(1, 'Error: no host name provided')

    if opts.user and not opts.passwd:
        opts.passwd = raw_input('passwd: ')

    if opts.user:
        creds = (opts.user, opts.passwd)
    else:
        creds = None

    x509 = {
        'cert_file' : 'C:/tmp/wbem_server.crt',
        'key_file' : 'C:/tmp/wbem_client.crt',
    }


    for a in args:
        c = pywbem.WBEMConnection(a, creds=creds, x509=x509)

        isn = c.EnumerateInstanceNames('CIM_Processor')

        for nm in isn:
            try:
                p = c.GetInstance(nm)
                print '-'*40
                print 'Name:', p['Name'].strip()
                print 'Load in percent:', p['LoadPercentage']
                for k,v in p.items():
                    print k, v
            except pywbem.cim_operations.CIMError as ex:
                pass


    oss.exit(0)


if __name__ == "__main__":
    main(oss.argv)
