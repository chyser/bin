#!/usr/bin/env python
"""
Library for accessinf data from REST services

"""

import xmlparse as xp
import osscripts as oss

import urllib
import sdchttplib2 as httplib2
import socket
import yaml


KEY_PATH_CLIENT = '/opt/sdc/ws/keys/ws_client.crt.pem'
KEY_PATH_ROOTCA = '/opt/sdc/ws/keys/root.ca.crt.pem'

WS_CLIENT_USER = 'ws_client'
WS_CLIENT_PASSWD = 'fdf5sa9)ertvw54%$#hg@qlg'

class RESTException(Exception):
    def __init__(self, p1, status=None):
        Exception.__init__(self, p1)
        self.status = status


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage restservice.py [options] <url>

    get data from and http service

    """
    args, opts = oss.gopt(oss.argv[1:], [('y', 'yaml'), ('x', 'xml'), ('j', 'json'), ('r', 'raw')], [], main.__doc__)

    if opts.yaml:
        print getDataYaml(args[0])
    elif opts.xml:
        if opts.raw:
            print getData(args[0], contentType='text/xml')
        else:
            print getDataXml(args[0])
    elif opts.json:
        print getDataJson(args[0])
    else:
        print getDataText(args[0])


#-------------------------------------------------------------------------------
def majorVer(version):
#-------------------------------------------------------------------------------
    return version.split('.')[0]


#-------------------------------------------------------------------------------
def getData(url, condition=None, contentType='text/plain'):
#-------------------------------------------------------------------------------
    """ wrapper for accessing webservice data from 'url'
    """

    hdrs = {'content-type' : contentType}

    if condition is not None:
        hdrs.update({'If-None-Match' : str(condition)})

    http = httplib2.Http()
    http.add_certificate(None, KEY_PATH_CLIENT, 'localhost')
    http.add_server_certificates(KEY_PATH_ROOTCA, httplib2.CERT_REQUIRED)
    http.add_credentials(WS_CLIENT_USER, WS_CLIENT_PASSWD)

    try:
        rsp, content = http.request(url, 'GET', headers=hdrs)
    except socket.error, ex:
        raise RESTException(ex)

    if rsp['status'] == '200':
        return content

    if rsp['status'] == '304':
        return None

    raise RESTException('url="%s" status="%s"' % (url, rsp['status']), rsp['status'])


def getDataYaml(url, condition=None, contentType='text/x-yaml'):
    content = getData(url, condition, contentType)
    return yaml.load(content) if content else None

def getDataJson(url, condition=None, contentType='application/json'):
    return getData(url, condition, contentType)

getDataText = getData

def getDataXml(url, condition=None, contentType='text/xml'):
    content = getData(url, condition, contentType)
    return xp.xmlNode(content) if content else None


#-------------------------------------------------------------------------------
def delete(url):
#-------------------------------------------------------------------------------
    try:
        getDataText(url)
    except RESTException:
        pass


#-------------------------------------------------------------------------------
def getDataList(url, tag, condition=None, resp=0):
#-------------------------------------------------------------------------------
    """ get data and return a list from a simple xml node and children relationship
    """
    xn = getDataXml(url, condition, 0, resp)
    return xn.findChildren(tag)


#-------------------------------------------------------------------------------
def putData(url, data=None, **kw):
#-------------------------------------------------------------------------------
    """ 'POST's 'data' to 'url'
        data : a dictionary

    """
    http = httplib2.Http()
    http.add_certificate(None, KEY_PATH_CLIENT, 'localhost')
    http.add_server_certificates(KEY_PATH_ROOTCA, httplib2.CERT_REQUIRED)
    http.add_credentials(WS_CLIENT_USER, WS_CLIENT_PASSWD)

    if data is None:
        data = kw
    body = urllib.urlencode(data)
    rsp, cnt = http.request(url, 'POST', body)
    return rsp, cnt


if __name__ == '__main__':
    main(oss.argv)


