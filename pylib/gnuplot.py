import sys
import os
import types

import osscripts as oss

import sys
import time

if sys.platform == 'win32':
    #GNUPLOT = 'C:/workspace/gnuplot/gnuplot/bin/pgnuplot.exe'
    GNUPLOT = 'C:/workspace/gnuplot/gnuplot1/binary/pgnuplot.exe'
    if not oss.exists(GNUPLOT):
        GNUPLOT = "pgnuplot.exe"
else:
    GNUPLOT = "gnuplot"

class GnuPlotException(Exception): pass

#-------------------------------------------------------------------------------
class PlotObject(object):
#-------------------------------------------------------------------------------
    """ base class for plot objects, the things that get plotted
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, gp):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(PlotObject, self).__init__()
        self.gp = gp

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def plot(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass


#-------------------------------------------------------------------------------
class DataGroup(PlotObject):
#-------------------------------------------------------------------------------
    """ the data group represents a number of things to plot.
    """
    fni = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, gp, options="", dbglvl=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(DataGroup, self).__init__(gp)
        self.lst = []
        #self.fni = 0
        self.dbglvl = dbglvl
        self.options = options

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setOptions(self, opt):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.options = self.options + ' ' + opt

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _pl(self, otf, itm):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if itm is None:
            otf.write('\n')
        elif isinstance(itm, tuple) or isinstance(itm, list):
            for i in itm:
                otf.write(str(i) + ' ')
            otf.write('\n')
        else:
            otf.write(str(itm) + '\n')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, lst, title='', lineStyle='', options=None, optmerge=False):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add a file or list to the data group

            lst can be a file containing the data, or a list of numbers or a
            list of tuples.
        """

        opt = self.options if options is None else (self.options + ' ' + options if optmerge else options)
        if title:      opt += ' title "%s"' % title
        if lineStyle:  opt += ' ls %d' % lineStyle

        if isinstance(lst, types.StringType):
            self.lst.append((lst, opt))

        fn = "/tmp/tgpl_%03d.dat" % self.fni
        oss.rm(fn)
        DataGroup.fni += 1

        with open(fn, 'w') as otf:
            for i in lst:
                self._pl(otf, i)

        if self.dbglvl > 0:
            with open(fn) as inf:
                for line in inf:
                    print line.strip()

        self.lst.append((fn, opt))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def plot(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        for fn, opt in self.lst:
            s.append("'%s' %s" % (fn, opt))
        self.gp.cmd("plot " + ','.join(s))


#-------------------------------------------------------------------------------
class StackedPlot(PlotObject):
#-------------------------------------------------------------------------------
    """ add subsequent lines/data to prior data
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, gp):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(StackedPlot, self).__init__(gp)
        self.vals = []
        self.base = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def plot(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        dg = DataGroup(self.gp)
        base = [0]*len(self.vals[0][0])

        for v, options in self.vals:
            for idx, val in enumerate(v):
                base[idx] += val
            dg.add(base, "with filledcurves x1 " + options)

        #dg.reverse()
        dg.plot()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add(self, lst, options=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.vals.append((lst, options))


#-------------------------------------------------------------------------------
class gnuplot(object):
#-------------------------------------------------------------------------------
    """ object representing the gnuplot program providing all control
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, xsize=1500, ysize=1000, dbglvl=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        super(gnuplot, self).__init__()
        self.gp = os.popen(GNUPLOT, 'w')
        self.dbglvl = dbglvl
        self.xsize = xsize
        self.ysize = ysize

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmd(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print >> self.gp, s
        self.gp.flush()
        if self.dbglvl > 0:
            print s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def close(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.gp.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def plotFile(self, fname, options=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmd("plot '%s' %s" % (fname, options))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _pl(self, otf, itm):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(itm, tuple) or isinstance(itm, list):
            for i in itm:
                print >> otf, i,
            print >> otf
        else:
            print >> otf, itm

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def plot(self, v, options=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(v, PlotObject):
            v.plot()
        elif isinstance(v, list) or isinstance(v, tuple):
            gpd = DataGroup(self)
            gpd.add(v, options)
            gpd.plot()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set(self, s):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.cmd("set " + s)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def size(self, x, y):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.xsize = x
        self.ysize = y

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xrange(self, max, min=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if min == max:
            raise GnuPlotException("min can't be equal to max")
        self.set("xrange ['%s':'%s']" % (str(min), str(max)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def yrange(self, max, min=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if min == max:
            raise GnuPlotException("min can't be equal to max")
        self.set("yrange ['%s':'%s']" % (str(min), str(max)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def x2range(self, max, min=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if min == max:
            raise GnuPlotException("min can't be equal to max")
        self.set("x2range ['%s':'%s']" % (str(min), str(max)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def y2range(self, max, min=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if min == max:
            raise GnuPlotException("min can't be equal to max")
        self.set("y2range ['%s':'%s']" % (str(min), str(max)))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def title(self, title, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('title "%s" %s' % (title, extra))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def xlabel(self, label, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('xlabel "%s" %s' % (label, extra))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def ylabel(self, label, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('ylabel "%s" %s' % (label, extra))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def x2label(self, label, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('x2label "%s" %s' % (label, extra))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def y2label(self, label, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('y2label "%s" %s' % (label, extra))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def createLineStyle(self, idx, lineType, lineColor=None, lineWidth=None, pointType=None, pointSize=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = '%d ' % idx
        if lineType:   s += 'lt %d ' % lineType
        if lineColor:  s += 'lc rgbcolor "%s" ' % lineColor
        if lineWidth:  s += 'lw %6.3f ' % lineWidth
        if pointType:  s += 'pt %d ' % pointType
        if pointSize:  s += 'ps %6.3f ' % pointSize

        self.set('style line %s' % s)
        return idx

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def output(self, fname, transparent=False, crop=False, linewidth=1, extra=""):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = 'linewidth %d ' % linewidth
        if transparent:  s  += 'transparent '
        if crop:         s += 'crop '
        self.cmd("set terminal png enhanced truecolor %s size %d,%d %s; set output '%s'" % (s, self.xsize, self.ysize, extra, fname))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test(self, typ, fname):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.set('terminal ' + typ)
        self.output(fname)
        self.cmd('test')


#-------------------------------------------------------------------------------
def main(argv):
#-------------------------------------------------------------------------------
    import statistics as ss
    gp = gnuplot()


    sp = StackedPlot(gp)
    sp.add([1, 2, 1, 4, 2, 3, 2, 2, 1], "title 'm1' lt 2 lw 3")
    sp.add([2, 1, 4, 2, 3, 2, 2, 4, 4], "title 'm2' lt 3 lw 3")
    sp.add([0, 3, 2, 2, 3, 1, 0, 1, 4], "title 'm3' lt 5 lw 3")
    gp.plot(sp)

    raw_input()


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    main(sys.argv)



