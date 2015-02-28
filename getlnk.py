import pylib.osscripts as oss


oss.cd('/home/chrish/tmp')
for f in oss.ls('*.st'):
    d = f.split('.')[:-3]
    f = '.'.join(d) + '.html'
    d = f.split('_')
    nm = d[0]
    f = '_'.join(d[1:])
    print 'http://xhamster.com/movies/' + nm  + '/' + f
