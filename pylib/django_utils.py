#!/usr/bin/env python
"""
Library:

"""

import base64
try:
    from django.http import HttpResponse
    from django.shortcuts import render_to_response, get_object_or_404
except ImportError:
    if __name__ != '__main__':
        raise

#-------------------------------------------------------------------------------
class basicHTTPAuthenticated(object):
#-------------------------------------------------------------------------------
    """ decorator for basic HTTP authentication
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, authenticationRealm, dbModel):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ dbModel must be an sql table with at least 'user' and 'passwd' fields
        """
        object.__init__(self)
        self.authenticationRealm = authenticationRealm
        self.dbModel = dbModel

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def authenticate(self, request):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            authType, value = request.META.get('HTTP_AUTHORIZATION', 'none').split()
            uname, passwd = base64.b64decode(value).split(':')

            usd = get_object_or_404(self.dbModel, user=uname)
            print authType
            print usd
            if authType.lower() == 'basic' and usd.passwd == passwd:
                return None

            raise ValueError('incorrect user/passwd format')
        except (ValueError, TypeError):
                pass

        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="%s"' % self.authenticationRealm
        return response

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __call__(self, decoratedFunction):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def wrapper(request, *args, **kwds):
            response = self.authenticate(request)
            if response is not None:
                return response

            return decoratedFunction(request, *args, **kwds)

        return wrapper


#-------------------------------------------------------------------------------
class basicHTTPAuthenticatedMember(basicHTTPAuthenticated):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __call__(self, decoratedMember):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def wrapper(mself, request, *args, **kwds):
            response = self.authenticate(request)
            if response is not None:
                return response

            return decoratedMember(mself, request, *args, **kwds)

        return wrapper



#-------------------------------------------------------------------------------
def makeTable(items, cls="table", rcls="row", tattr=''):
#-------------------------------------------------------------------------------
    ln = len(items)
    print items

    s = ['<table class="%s" %s>' % (cls, tattr)]
    if ln < 6:
        for i in items:
            s.append('    <tr class="%s"><td>%s</td></tr>' % (rcls, i))

    elif ln < 13:
        col = (ln + 2) / 3
        for i in range(col):
            s.append('    <tr class="%s">' % rcls)
            for idx in range(0,ln,col):
                try:
                    s.append('        <td>%s</td>' % (items[idx+i]))
                except IndexError:
                    s.append('        <td>&nbsp</td>')
            s.append('    </tr>')

    else:
        col = (ln + 5) / 6
        for i in range(col):
            s.append('    <tr class="%s">' % rcls)
            for idx in range(0,ln,col):
                try:
                    s.append('        <td>%s</td>' % items[idx+i])
                except IndexError:
                    s.append('        <td>&nbsp</td>')
            s.append('    </tr>')

    s.append('</table>')
    print '\n'.join(s)
    return '\n'.join(s)


#-------------------------------------------------------------------------------
def mkListofListsH(items, empty=''):
#-------------------------------------------------------------------------------
    ln = len(items)
    if ln < 6:
        mcol = 1
    elif ln < 7:
        mcol = 3
    else:
        mcol = 6


    col = (ln + mcol - 1) / mcol
    lst = []
    for i in range(col):
        ll = []
        for idx in range(0,ln,col):
            try:
                ll.append(items[idx+i])
            except IndexError:
                ll.append(empty)
        lst.append(ll)

    return lst

#-------------------------------------------------------------------------------
def mkListofLists(items, empty='', max_col=10):
#-------------------------------------------------------------------------------
    ln = len(items)
    if ln < 7:
        mcol = 1
    elif ln < 19:
        mcol = 3
    elif ln < 37:
        mcol = 6
    else:
        mcol = 10

    if mcol > max_col:
        mcol = max_col

    col = (ln + mcol - 1) / mcol
    lst = []
    for idx in range(0,ln,col):
        ll = []
        for i in range(col):
            try:
                ll.append(items[idx+i])
            except IndexError:
                ll.append(empty)
        lst.append(ll)

    return lst


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester

    return 0

if __name__ == "__main__":
    import pylib.osscripts as oss
    arg, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    res = not __test__()

    import pprint
    pprint.pprint(mkListofLists(['test_%d' % i for i in range(int(arg[0]))]))
    print

    oss.exit(res)




