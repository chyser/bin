import xmlrpclib
import SimpleXMLRPCServer
import pylib.xmlparse as xp
import xml.dom.minidom as md

#-------------------------------------------------------------------------------
class PyRPCServerProxy(object):
#-------------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    class wrapper(object):
    #---------------------------------------------------------------------------
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __init__(self, method, proxy):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            self.method = method
            self.px = proxy

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        def __call__(self, *args):
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            bo = xmlrpclib.Binary()
            bo.data = self.px.otx.marshal('args', args)
            ret = self.method(bo)
            return self.px.xto.unmarshal_str(ret.data)[1]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, url="http://localhost:9091", newObj = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(PyRPCServerProxy, self).__init__()
        self.server = xmlrpclib.ServerProxy(url)
        self.otx = xp.ObjToXML(Rules = 0)
        self.xto = xp.XMLToObj(newObj = newObj)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __getattr__(self, attr):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        meth = getattr(self.server, attr, None)
        return PyRPCServerProxy.wrapper(meth, self)

#-------------------------------------------------------------------------------
class PyRPCServer(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, addr = ('', 9091), newObj=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(PyRPCServer, self).__init__()
        self.otx = xp.ObjToXML(Rules = 0)
        self.xto = xp.XMLToObj(newObj = newObj)

        self.instance = None
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer(addr)
        self.server.register_instance(self)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def serve_forever(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
         self.server.serve_forever()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _dispatch(self, name, binArg):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        bo = xmlrpclib.Binary()

        if name == 'help':
            ret =  "help called"
        elif name == 'listMeth':
            ret = []
            for i in dir(self.instance):
                if i[0] != '_':
                    ret.append(i)
        else:
            ## binArg is a binary tuple of any type of args
            args = self.xto.unmarshal_str(binArg[0].data)[1]
            meth = getattr(self.instance, name)
            ret = meth(*args)

        bo.data = self.otx.marshal('ret', ret)
        return bo

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def register_instance(self, instance):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.instance = instance


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    class boo(object):
        def __init__(self):
            self.s = "cool"

    class aidan(object):
        def __init__(self):
            pass

        def run(self, b):
            b.s = "run called"
            return b

    ps = PyRPCServer()
    ps.register_instance(aidan())
    ps.serve_forever()


