#!/usr/bin/env python
"""
Simple amqplib wrapper.

"""
import time
import amqplib.client_0_8 as amqp
import re
import logging
import socket


#-------------------------------------------------------------------------------
def parseAmqUrl(url):
#-------------------------------------------------------------------------------
    """ parses a ch defined url

    amq[s]://[user[:password]@]host/exchange[/routingkey]
    returns bool:ssl, str:user, str:passwd, str:host, str:exchange, str:routing_key
    """
    r = re.compile(r'^amq(s*)://(([^:]+)(:([^:]+))?@)?([^/:]+)(/([^/]+))?(/([^/]+))?$')
    try:
        g = r.match(url).groups()
        return g[0] == 's', g[2], g[4], g[5], g[7], g[9]
    except AttributeError:
        raise AMQP.AMQPException('illegal url')


#-------------------------------------------------------------------------------
def parseAmqUrlDict(url):
#-------------------------------------------------------------------------------
    """ returns a dict with non-None values set
    """
    ssl, userid, password, host, xchg, key = parseAmqUrl(url)
    d = {'ssl' : ssl, 'userid' : userid, 'password' : password, 'host' : host, 'xchg' : xchg, 'key' : key}
    for k, v in d.items():
        if v is None:  del d[k]
    return d


#-------------------------------------------------------------------------------
def createAmqUrl(host, ssl=None, user=None, passwd=None, xchg=None, key=None):
#-------------------------------------------------------------------------------
    pw = ':' + passwd if passwd else ''
    up = user + pw + '@' if user else ''
    k = '/' + key if key else ''
    xc = '/' + xchg + k if xchg else ''
    return 'amq%s://%s%s%s' % ('s' if ssl else '', up, host, xc)


#-------------------------------------------------------------------------------
class AMQP(object):
#-------------------------------------------------------------------------------
    """ can be used as a mixin with threading.Thread or standalone
    """

    class AMQPException(Exception): pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, url=None, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)

        ## default
        self.ssl = False
        self.userid = 'guest'
        self.password = 'guest'
        self.host = None
        self.xchg = 'sism'
        self.key = None
        self.type = 'topic'

        ## parameter sanity check
        assert set(kw.keys()).issubset(set(self.__dict__.keys())), "Incorrect Parameters AMQP object"

        ## set from url if specified
        if url is not None:
            self.__dict__.update(parseAmqUrlDict(url))

        ## set from function parameters, overridding any 'url' values
        self.__dict__.update(kw)

        ## allow creation of an empty object
        if self.host is None:
            self.ch = None
            return

        self.breakOut = False

        ## connect to AMQP server
        self.amqp_debug = False

        self.setup()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setup(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.conn = amqp.Connection(self.host, userid=self.userid, password=self.password, ssl=self.ssl)
        except socket.error:
            raise AMQP.AMQPException('connection failure')

        self.ch = self.conn.channel()
        self.ch.access_request('/data', active=True, write=True)
        self.ch.exchange_declare(self.xchg, self.type, auto_delete=True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def url(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return createAmqUrl(self.host, self.ssl, self.userid, self.password, self.xchg, self.key)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dbgMsg(self, msg, *args, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.amqp_debug:
            print '-'*40
            print '-- dbgMsg --'
            print 'exchange:', self.xchg
            for i in args:
                print i

            for k,v in kw.items():
                print k, ':', v

            print msg
            print '-'*40
        return 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sendMsg(self, msg, routing_key=None, hdrs=None, content_type='text/plain', **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        assert self.ch is not None, 'sendMsg called when channel not initialized'

        if hdrs is None: hdrs = {}
        if routing_key is None:
            routing_key = self.key

        assert routing_key is not None, 'sendMsg called with no routing_key nor default routing key'
        assert self.dbgMsg(msg, routing_key=routing_key, hdrs=hdrs, content_type=content_type, **kw)

        amsg = amqp.Message(msg, content_type=content_type, application_headers=hdrs, **kw)
        self.ch.basic_publish(amsg, self.xchg, routing_key=routing_key)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def recvSetup(self, routing_key="#", callback=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if callback is None:
            callback = self.callback
        qname = self.ch.queue_declare()[0]
        self.ch.queue_bind(qname, self.xchg, routing_key=routing_key)
        self.ch.basic_consume(qname, callback=callback)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def onNewMsg(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ default OnNewMsg callback simply displays message information
        """
        print '='*80
        for key, val in msg.properties.items():
            print '%s: %s' % (key, str(val))

        print '-'*8
        for key, val in msg.delivery_info.items():
            print '%s: %s' % (key, str(val))

        print '-'*8
        print msg.body

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def callback(self, msg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.onNewMsg(msg)
        msg.channel.basic_ack(msg.delivery_tag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def run(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        while self.ch.callbacks:
            if self.breakOut:
                break
            self.ch.wait()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def stop(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.breakOut = True

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.ch is not None:
            self.ch.close()

        if self.conn is not None:
            self.conn.close()


#-------------------------------------------------------------------------------
class AMQPLoggingHandler(logging.Handler):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, url=None, **kw):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        logging.Handler.__init__(self)
        self.mq = AMQP(url, **kw)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def emit(self, rec):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.mq.sendMsg(self.format(rec), content_type='text/plain')


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    """ usage: message.py [options] [message text]

        options:
           -u | --url <url>    : use a 'ch' url (def: no)

           -a | --addr <addr>  : specify network address of amqp server (def: localhost)
           -x | --xchg <xchg>  : specify the exchange (sism)
           -k | --key  <key>   : specify the key to use (def: #)

           -r | --recv         : receive messages
           -s | --ssl          : whether to use SSL

           -c | --content <ct> : specify content_type (def: text/plain)
           -m | --msgId <mid>  : message ID (def: node)

           -T | --TEST  : run unit tests
    """

    args, opts = oss.gopt(argv[1:], [('r','recv'), ('s','ssl'), ('T', 'TEST')], [('k','key'),
        ('a','addr'),  ('x','xchg'), ('u','url'), ('c', 'content'), ('m', 'msgId')], __doc__ + main.__doc__)

    if opts.TEST:
        return __test__()

    if opts.url is not None:
        mq = AMQP(opts.url)
    else:
        if opts.addr is None: opts.addr = 'localhost'
        if opts.xchg is None: opts.xchg = 'sism'
        mq = AMQP(host=opts.addr, xchg=opts.xchg, ssl=opts.ssl)

    if opts.key is None: opts.key = '#'

    if opts.recv:
        if opts.url:
            print "listening: %s/%s" % (opts.url, str(opts.key))
        else:
            print "listening: amq%s://%s/%s/%s" % ('s' if opts.ssl else '', opts.addr, opts.xchg, str(opts.key))

        if isinstance(opts.key, list):
            for k in opts.key:
                mq.recvSetup(k)
        else:
            mq.recvSetup(opts.key)

        mq.run()
    else:
        if not args:
            oss._usage(1, 'must supply a message')

        data = oss.stdin.read() if args[0] == '-' else ' '.join(args)
        if opts.content is None: opts.content = 'text/plain'
        if opts.msgId is None: opts.msgId = ''
        mq.sendMsg(data, routing_key=opts.key, content_type=opts.content, message_id=opts.msgId)

    oss.exit(0)


#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """ unit tests
    """

    try:
        from tester import Assert, AssertRecvException, TesterException
    except ImportError:
        from pylib.tester import Assert, AssertRecvException, TesterException

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://host/xchg')
    Assert(not ssl and user is None and pswd is None and host == 'host' and xchg == 'xchg' and key is None)
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://host/xchg')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amqs://host/xchg')
    Assert(ssl and user is None and pswd is None and host == 'host' and xchg == 'xchg' and key is None)
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amqs://host/xchg')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://host/xchg/key')
    Assert(not ssl and user is None and pswd is None and host == 'host' and xchg == 'xchg' and key == 'key')
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://host/xchg/key')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://user@host/xchg')
    Assert(not ssl and user == 'user' and pswd is None and host == 'host' and xchg == 'xchg' and key is None)
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://user@host/xchg')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://user:pswd@host/xchg')
    Assert(not ssl and user == 'user' and pswd == 'pswd' and host == 'host' and xchg == 'xchg' and key is None)
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://user:pswd@host/xchg')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://user@host/xchg/key')
    Assert(not ssl and user == 'user' and pswd is None and host == 'host' and xchg == 'xchg' and key == 'key')
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://user@host/xchg/key')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://user:pswd@host/xchg/key')
    Assert(not ssl and user == 'user' and pswd == 'pswd' and host == 'host' and xchg == 'xchg' and key == 'key')
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://user:pswd@host/xchg/key')

    ssl, user, pswd, host, xchg, key = parseAmqUrl('amq://user:pswd@host')
    Assert(not ssl and user == 'user' and pswd == 'pswd' and host == 'host' and xchg is None and key is None)
    Assert(createAmqUrl(host, ssl, user, pswd, xchg, key) == 'amq://user:pswd@host')

    AssertRecvException(AMQP.AMQPException, parseAmqUrl, ('amq://user:pswd@host/xchg/key/key',))

    if __debug__:
        try:
            AMQP(conn = 'connection')
            raise TesterException("Test Assert Failed " + "AMQP didn't recognize bad parameters")
        except AssertionError:
            pass


if __name__ == "__main__":
    try:
        import osscripts as oss
    except ImportError:
        import pylib.osscripts as oss

    main(oss.argv)


