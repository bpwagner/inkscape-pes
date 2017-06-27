#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Example of extensions template for inkscape

'''

import inkex       # Required
import simplestyle # will be needed here for styles support
import os          # here for alternative debug method only - so not usually required
# many other useful ones in extensions folder. E.g. simplepath, cubicsuperpath, ...

from math import cos, sin, radians
import sys

__version__ = '0.2'

inkex.localize()

debug = True

### Your helper functions go here
def points_to_svgd(p, close=True):
    """ convert list of points (x,y) pairs
        into a closed SVG path list
    """
    f = p[0]
    p = p[1:]
    svgd = 'M%.4f,%.4f' % f
    for x in p:
        svgd += 'L%.4f,%.4f' % x
    if close:
        svgd += 'z'
    return svgd

def points_to_bbox(p):
    """ from a list of points (x,y pairs)
        - return the lower-left xy and upper-right xy
    """
    llx = urx = p[0][0]
    lly = ury = p[0][1]
    for x in p[1:]:
        if   x[0] < llx: llx = x[0]
        elif x[0] > urx: urx = x[0]
        if   x[1] < lly: lly = x[1]
        elif x[1] > ury: ury = x[1]
    return (llx, lly, urx, ury)

def points_to_bbox_center(p):
    """ from a list of points (x,y pairs)
        - find midpoint of bounding box around all points
        - return (x,y)
    """
    bbox = points_to_bbox(p)
    return ((bbox[0]+bbox[2])/2.0, (bbox[1]+bbox[3])/2.0)

def point_on_circle(radius, angle):
    " return xy coord of the point at distance radius from origin at angle "
    x = radius * cos(angle)
    y = radius * sin(angle)
    return (x, y)

def draw_SVG_circle(parent, r, cx, cy, name, style):
    " structre an SVG circle entity under parent "
    circ_attribs = {'style': simplestyle.formatStyle(style),
                    'cx': str(cx), 'cy': str(cy), 
                    'r': str(r),
                    inkex.addNS('label','inkscape'): name}
    circle = inkex.etree.SubElement(parent, inkex.addNS('circle','svg'), circ_attribs )


def MakeSTL():
    return

def getUnittouu(self, param):
    " for 0.48 and 0.91 compatibility "
    try:
        return inkex.unittouu(param)
    except AttributeError:
        return self.unittouu(param)

def calc_unit_factor(self):
    """ return the scale factor for all dimension conversions.
        - The document units are always irrelevant as
          everything in inkscape is expected to be in 90dpi pixel units
    """
    # namedView = self.document.getroot().find(inkex.addNS('namedview', 'sodipodi'))
    # doc_units = self.getUnittouu(str(1.0) + namedView.get(inkex.addNS('document-units', 'inkscape')))
    unit_factor = self.getUnittouu(str(1.0) + self.options.units)
    return unit_factor

### Your main function subclasses the inkex.Effect class

class Myextension(inkex.Effect): # choose a better name
    
    def __init__(self):
        " define how the options are mapped from the inx file "
        inkex.Effect.__init__(self) # initialize the super class
        
        # Two ways to get debug info:
        # OR just use inkex.debug(string) instead...
        try:
            self.tty = open("/dev/tty", 'w')
        except:
            self.tty = open(os.devnull, 'w')  # '/dev/null' for POSIX, 'nul' for Windows.
            # print >>self.tty, "gears-dev " + __version__
            
        # Define your list of parameters defined in the .inx file
        # self.OptionParser.add_option("-s", "--GenSTL",
        #                              action="store", type="inkbool",
        #                              dest="GenSTL", default=False,
        #                              help="Generate STL File")
        # self.OptionParser.add_option("-l", "--GenLaser",
        #                              action="store", type="inkbool",
        #                              dest="GenLaser", default=False,
        #                              help="Generate laser File")
        # self.OptionParser.add_option("-t", "--GenStitch",
        #                              action="store", type="inkbool",
        #                              dest="GenStitch", default=False,
        #                              help="Generate Stitching File")
        self.OptionParser.add_option('--r1x',action='store',type='float', dest='r1x',default=0.0,
                                     help='Registration 1 offset x')
        self.OptionParser.add_option('--r1y', action='store', type='float', dest='r1y', default=0.0,
                                     help='Registration 1 offset y')
        self.OptionParser.add_option('--r2x', action='store', type='float', dest='r1x', default=0.0,
                                     help='Registration 2 offset x')
        self.OptionParser.add_option('--r2y', action='store', type='float', dest='r1y', default=0.0,
                                     help='Registration 2 offset y')

        self.OptionParser.add_option("-d", "--dir",
                                     action="store", type="string",
                                     dest="dir", default='.',
                                     help="Enter full directory path here.")

        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")

        return

### -------------------------------------------------------------------
### This is your main function and is called when the extension is run.
    
    def effect(self):
        # Just for 'fun' - report Python version
        if debug:
            cur_version = sys.version_info
            message = "Python version: " + str(cur_version) + "\n"
            inkex.debug(message)
        
        # check for correct number of selected objects and return a translatable errormessage to the user
        if len(self.options.ids) >= 1:
            inkex.errormsg(("This extension requires at least 1 selected path."))
            exit()

        # gather incoming params and convert
        r1x = self.options.r1x
        r1y = self.options.r1y
        r2x = self.options.r2x
        r2y = self.options.r2y

        dir = self.options.dir

        inkex.debug(r1x, r1y, r2x, r2y)
        inkex.debug(dir)

        # what page are we on
        page_id = self.options.active_tab # sometimes wrong the very first time


if __name__ == '__main__':
    e = Myextension()
    e.affect()

# Notes

