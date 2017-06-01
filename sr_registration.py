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


def draw_SVG_line((x1, y1),(x2, y2),line_width , name, parent):
    style = { 'stroke': '#000000', 'stroke-width':str(line_width), 'stroke-linecap':'round'}
    line_attribs = {'style':simplestyle.formatStyle(style),
                    inkex.addNS('label','inkscape'):name,
                    'd':'M '+str(x1)+','+str(y1)+' '+str(x2)+','+str(y2)}
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )
    
def addText(node,x,y,text, transform=None):
    new = inkex.etree.SubElement(node,inkex.addNS('text','svg'))
    s = {'text-align': 'center', 'vertical-align': 'top','text-anchor': 'middle',
    'font-size': '20.0', 'fill-opacity': '1.0', 'stroke': 'none',
        'font-weight': 'normal', 'font-style': 'normal', 'fill': '#000'}
    new.set('style', simplestyle.formatStyle(s))
    if not transform==None:
        new.set('transform', str(transform))
    new.set('x', str(x))
    new.set('y', str(y))
    new.text = str(text)
    

def reg_group(p1, p2, p3, p4, line_width, name, parent):
    grp_attribs = {inkex.addNS('label','inkscape'):name}
    grp = inkex.etree.SubElement(parent, 'g', grp_attribs)#the group to put everything in
    draw_SVG_line(p1, p2,line_width, name + '_a', grp)
    draw_SVG_line(p3, p4,line_width, name + '_b', grp)
    addText(grp, p1[0] + 20, p1[1] + 5, name, None)

class Reg_mark(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        
        self.OptionParser.add_option('--unit',action='store',type='string', dest='unit',default='mm',help='units of measurement')
        self.OptionParser.add_option('--reg_offset',action='store',type='float', dest='reg_offset',default=0,help='Offset (vert distance of how far apart)')
        self.OptionParser.add_option('--reg_size',action='store',type='float', dest='reg_size',default=0,help='Size of registration marks')
        self.OptionParser.add_option('--reg_line_width',action='store',type='float', dest='reg_line_width',default=0,help='Line width of registration marks')
        
        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",action="store", 
            type="string",dest="active_tab", 
            default='title', help="Active tab.")
            
    
    def getUnittouu(self, param):
        " for 0.48 and 0.91 compatibility "
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)


    def effect(self):
        svg = self.document.getroot()
        
        unit=self.options.unit        
        offset = self.getUnittouu(str(self.options.reg_offset) + unit)
        reg_size = self.getUnittouu(str(self.options.reg_size) + unit)
        line_width = self.getUnittouu(str(self.options.reg_line_width) + unit)
        
        curr_layer = self.current_layer
        
        width  = self.getUnittouu(svg.get('width'))
        height = self.getUnittouu(svg.attrib['height'])
        
        center = (width/2.,height/2.0)
        
        p1 = (center[0], center[1] - offset - reg_size)
        p2 = (center[0], center[1] - offset + reg_size)
        p3 = (center[0]-reg_size, center[1] - offset)
        p4 = (center[0]+reg_size, center[1] - offset)

        reg_group(p1,p2,p3,p4, line_width, 'R1', curr_layer)
        
        p1 = (center[0], center[1] + offset - reg_size)
        p2 = (center[0], center[1] + offset + reg_size)
        p3 = (center[0]-reg_size, center[1] + offset)
        p4 = (center[0]+reg_size, center[1] + offset)

        reg_group(p1,p2,p3,p4, line_width, 'R2', curr_layer)

if __name__ == '__main__':

    e = Reg_mark()
    e.affect()
