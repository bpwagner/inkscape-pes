#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Example of extensions template for inkscape

'''

import inkex       # Required
import simplestyle # will be needed here for styles support
import os          # here for alternative debug method only - so not usually required
import os.path
# many other useful ones in extensions folder. E.g. simplepath, cubicsuperpath, ...

from math import cos, sin, radians
import sys
import simplepath
import simpletransform
import cubicsuperpath
import numpy as np
import re
from sr_export_PES import make_pes
#import matplotlib.pyplot as plt

NSS = {
u'sodipodi' :u'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
u'cc'       :u'http://creativecommons.org/ns#',
u'ccOLD'    :u'http://web.resource.org/cc/',
u'svg'      :u'http://www.w3.org/2000/svg',
u'dc'       :u'http://purl.org/dc/elements/1.1/',
u'rdf'      :u'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
u'inkscape' :u'http://www.inkscape.org/namespaces/inkscape',
u'xlink'    :u'http://www.w3.org/1999/xlink',
u'xml'      :u'http://www.w3.org/XML/1998/namespace'
}


__version__ = '0.2'

inkex.localize()

debug = True

### Your helper functions go here

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

def normalize_pts(pts, minSize, maxSize):
    pts = np.array(pts)

    new_pts = []
    i = 0
    best_size = (maxSize + minSize)/2.0

    while i < pts.shape[0]-1:
        point1 = pts[i]
        point2 = pts[i + 1]

        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        vector = [(x2 - x1),(y2 - y1)]
        #catch divide by zero...
        if dist < 0.001:
            dist = 0.001
        unit_vector = [vector[0] / dist, vector[1] / dist]
        #print point1, point2, dist
        #create intermediary points if dist > maxsize
        if dist >= maxSize:
            count = int(dist/best_size) +1
            # not needed because j=0 ----- new_pts.append(point1)
            for j in range(count):
                temp_pt = [x1 + (best_size * j * unit_vector[0]), y1 + (j* best_size * unit_vector[1])]
                #print 'new pt"', temp_pt
                new_pts.append(temp_pt)
            new_pts.append(point2)
        #skip over really close points
        elif dist <= minSize :
            new_pts.append(point1)
            #print 'point skipped', point2
            nextPoint = 2
            while dist < minSize:
                try:
                    point2 = pts[i + nextPoint]
                except:
                    break
                x2, y2 = pts[i + nextPoint]
                dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                vector = [(x2 - x1), (y2 - y1)]
                if dist < 0.001:
                    dist = 0.001
                unit_vector = [vector[0] / dist, vector[1] / dist]
                dist = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
                #print 'trying', point2, dist
                nextPoint = nextPoint + 1
            # create intermediary points if dist > maxsize
            if dist >= maxSize:
                count = int(dist / best_size) +1
                # not needed because j=0 ----- new_pts.append(point1)
                for j in range(count):
                    temp_pt = [x1 + (best_size * j * unit_vector[0]), y1 + (j * best_size * unit_vector[1])]
                    #print 'new pt"', temp_pt
                    new_pts.append(temp_pt)
                new_pts.append(point2)
            else:
                #print 'using', point2, dist
                new_pts.append(point2)
            i = i + nextPoint - 1
        #otherwise points are good
        else:
            new_pts.append(point1)
            new_pts.append(point2)
        i = i+2

    return np.array(new_pts)




def getzigzag(pts):
    pts = np.array(pts)
    #x, y = pts.T
    # plt.plot(x, y, 'ro')
    #plt.plot(x, y, 'b-')

    zigzag = []

    for i in range(len(pts) - 1):
        d = 5.0
        point1 = pts[i]
        point2 = pts[i + 1]
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        mid = (point1 + point2) / 2.0
        mid = [mid[0], mid[1]]
        perp_vector = [(y1 - y2), (x2 - x1)]

        denom = np.sqrt((y1 - y2) ** 2 + (x2 - x1) ** 2)
        if denom > 10000.0:
            denom = 10000.0

        dist = d / denom
        if dist > 10000.0:
            dist = 10000.0

        temp = [dist * perp_vector[0], dist * perp_vector[1]]
        point3 = [point1[0] + temp[0], point1[1] + temp[1]]
        point4 = [mid[0] - temp[0], mid[1] - temp[1]]
        zigzag.append(point3)
        zigzag.append(point4)

    return zigzag

def is_empty(val):
    if val is None:
        return True
    else:
        return len(str(val)) == 0




### Your main function subclasses the inkex.Effect class
class Embroider(inkex.Effect): # choose a better name
    
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
        self.OptionParser.add_option('--thread_offset',action='store',type='float', dest='thread_offset',default=0.0,
                                     help='Thread zigzag offset from path')
        self.OptionParser.add_option("-z", "--zigzag",
                                     action="store", type="string",
                                     dest="zigzag", default=False,
                                     help="Check to produce zigzag stitches")
        self.OptionParser.add_option('--r1x',action='store',type='float', dest='r1x',default=0.0,
                                     help='Registration 1 offset x')
        self.OptionParser.add_option('--r1y', action='store', type='float', dest='r1y', default=0.0,
                                     help='Registration 1 offset y')
        self.OptionParser.add_option('--r2x', action='store', type='float', dest='r2x', default=0.0,
                                     help='Registration 2 offset x')
        self.OptionParser.add_option('--r2y', action='store', type='float', dest='r2y', default=0.0,
                                     help='Registration 2 offset y')

        self.OptionParser.add_option("-f", "--filename",
                                     action="store", type="string",
                                     dest="filename", default='.',
                                     help="Enter filename here.")
        self.OptionParser.add_option("-d", "--dir",
                                     action="store", type="string",
                                     dest="dir", default='.',
                                     help="Enter full directory path here.")

        self.OptionParser.add_option("-o", "--overwrite",
                                     action="store", type="string",
                                     dest="overwrite", default=False,
                                     help="Check to overwrite file")

        self.OptionParser.add_option("-g", "--debug",
                                     action="store", type="string",
                                     dest="debug", default=False,
                                     help="Check to show debug messages")

        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                     action="store", type="string",
                                     dest="active_tab", default='title', # use a legitmate default
                                     help="Active tab.")

        return

    def uutomm(self, pts):
        return pts / (self.document.__uuconv['mm'] / self.document.__uuconv[self.document.getDocumentUnit()])




    def validate_path(self):
        # The user must supply a directory to export:
        # No directory separator at the path end:
        if self.options.dir[-1] == '/' or self.options.dir[-1] == '\\':
            self.options.dir = self.options.dir[0:-1]
        # Test if the directory exists:
        if not os.path.exists( self.options.dir ):
           inkex.debug('The path "%s" does not exists.') % self.options.dir
           return False
        return True

    def get_registration(self, group, name):
    #find the registration marks and pass them
        trans = ''
        d='not found'
        layers = self.document.findall('{http://www.w3.org/2000/svg}g')
        for layer in layers:
            #get the groups in the layers
            groups = layer.findall('{http://www.w3.org/2000/svg}g')
            for group in groups:
                #get the translation for the group if there is one
                group_trans = ''
                group_trans = group.get("transform")
                #get the paths in that group
                paths = group.findall('{http://www.w3.org/2000/svg}path')
                for path in paths:
                    path_name = path.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label', None)
                    if path_name == name:
                        #inkex.debug(path_name)
                        d = path.get("d")
                        trans = group_trans
                        #inkex.debug(trans)
                        #inkex.debug(d)
                        break

        if d == 'not found':
            inkex.debug('*** CRITICAL ERROR - UNABLE TO FIND REGISTRATION MARKS ON FIRST LEVEL ***')
            return (-1,-1)
        else:
            # deal with moving r1 and r2.  Only allow translation of the group, no skew, rotation, etc.
            if trans != None:
                trans = trans.strip()
                result = re.match("(translate|scale|rotate|skewX|skewY|matrix)\s*\(([^)]*)\)\s*,?", trans)
                # -- translate --
                if result.group(1) == "translate":
                    args = result.group(2).replace(',', ' ').split()
                    dx = float(args[0])
                    if len(args) == 1:
                        dy = 0.0
                    else:
                        dy = float(args[1])
                else:
                    dx = 0.
                    dy = 0.
            else:
                dx = 0.
                dy = 0.


            c1, p1, p2 = d.split(" ")
            x1, y1 = p1.split(",")
            x1 = float(x1) + dx
            y1 = float(y1) + dy
            dx2, dy2 = p2.split(",")
            x2 = x1 + float(dx2)
            y2 = y1 + float(dy2)

        #inkex.debug('get registration')
        #inkex.debug(trans)
        #inkex.debug(name + ' ' + d)
        return ((x1 + x2)/2, (y1 + y2)/2)

    def get_theta(self, p1, p2):
        #find the angle between two points...
        from math import atan2, pi
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        rads = atan2(-dy, dx)
        rads %= 2 * pi
        return rads

    def get_translated_points(self, pts, r1_ink, r2_ink, r1_emb, r2_emb):
        #this fuction takes pts and makes new_pts by scaling,translating and rotating based upon the reg points

        r1_ink = np.array(r1_ink)
        r2_ink = np.array(r2_ink)
        r1_emb = np.array(r1_emb)
        r2_emb = np.array(r2_emb)
        pts = np.array(pts)

        # calculate length of lines
        dist_1 = np.linalg.norm(r1_ink - r2_ink)
        dist_2 = np.linalg.norm(r1_emb - r2_emb)
        # scale should be 1...
        scale_factor = dist_2 / dist_1

        # find the midpoints of the registration points so we can get a true offfset
        # for the translation matrix
        # #midpoints
        mid_1 = (r1_ink + r2_ink) / 2.0
        mid_2 = (r1_emb + r2_emb) / 2.0

        # translate the pts to embroidery machine points
        # first move all the points to homogenius coordinates
        # add a 1 column to the end of points
        h_pts = np.array(pts)
        temp = np.ones((len(pts), 1))
        h_pts = np.append(h_pts, temp, axis=1)

        # identity matrix
        ident = np.zeros((3, 3), dtype=float)
        ident[0][0] = 1.0
        ident[1][1] = 1.0
        ident[2][2] = 1.0

        # flipy matrix
        # not used
        fy = np.zeros((3, 3), dtype=float)
        fy[0][0] = 1.0
        fy[1][1] = -1.0
        fy[2][2] = 1

        # Scale Matrix
        s = np.zeros((3, 3), dtype=float)
        s[0][0] = scale_factor
        s[1][1] = scale_factor
        s[2][2] = 1

        # translation matrix to origin
        to_dx = -mid_1[0]
        to_dy = -mid_1[1]

        to = np.zeros((3, 3), dtype=float)
        to[0][0] = 1
        to[0][2] = to_dx
        to[1][1] = 1
        to[1][2] = to_dy
        to[2][2] = 1

        # translation matrix
        t_dx = mid_2[0]
        t_dy = mid_2[1]

        t = np.zeros((3, 3), dtype=float)
        t[0][0] = 1
        t[0][2] = t_dx
        t[1][1] = 1
        t[1][2] = t_dy
        t[2][2] = 1

        r = np.zeros((3, 3), dtype=float)
        # find angle of first
        theta_coord = self.get_theta(mid_1, r2_ink)
        # find angle of offset
        theta_offset = self.get_theta(mid_2, r2_emb)
        # combine them and wrap around the circle
        theta = (theta_coord - theta_offset) % (2 * np.pi)

        # theta = np.pi/3; #test, 60degrees
        r[0][0] = np.cos(theta)
        r[0][1] = -1 * np.sin(theta)
        r[1][0] = np.sin(theta)
        r[1][1] = np.cos(theta)
        r[2][2] = 1

        # move points to origin
        # set up like this for testing
        m = ident
        m = np.dot(m, to)
        new_pts = []
        new_h_pts = []
        for h_pt in h_pts:
            trans = np.reshape(h_pt, (3, 1))
            new_pt = np.dot(m, trans)
            pt = (new_pt[0][0] / new_pt[2][0], new_pt[1][0] / new_pt[2][0])
            new_h_pt = (new_pt[0][0], new_pt[1][0], new_pt[2][0])
            new_pts.append(pt)
            new_h_pts.append(new_h_pt)
        new_pts = np.array(new_pts)
        h_pts = new_h_pts

        # scale it at the origin
        # set up like this for testing
        m = ident
        m = np.dot(m, s)
        new_pts = []
        new_h_pts = []
        for h_pt in h_pts:
            trans = np.reshape(h_pt, (3, 1))
            new_pt = np.dot(m, trans)
            pt = (new_pt[0][0] / new_pt[2][0], new_pt[1][0] / new_pt[2][0])
            new_h_pt = (new_pt[0][0], new_pt[1][0], new_pt[2][0])
            new_pts.append(pt)
            new_h_pts.append(new_h_pt)
        new_pts = np.array(new_pts)
        h_pts = new_h_pts

        # rotate it at the origin
        # set up like this for testing
        m = ident
        m = np.dot(m, r)
        new_pts = []
        new_h_pts = []
        for h_pt in h_pts:
            trans = np.reshape(h_pt, (3, 1))
            new_pt = np.dot(m, trans)
            pt = (new_pt[0][0] / new_pt[2][0], new_pt[1][0] / new_pt[2][0])
            new_h_pt = (new_pt[0][0], new_pt[1][0], new_pt[2][0])
            new_pts.append(pt)
            new_h_pts.append(new_h_pt)
        new_pts = np.array(new_pts)
        h_pts = new_h_pts

        # move it to where it needs to be
        # set up like this for testing
        m = ident
        m = np.dot(m, t)
        new_pts = []
        new_h_pts = []
        for h_pt in h_pts:
            trans = np.reshape(h_pt, (3, 1))
            new_pt = np.dot(m, trans)
            pt = (new_pt[0][0] / new_pt[2][0], new_pt[1][0] / new_pt[2][0])
            new_h_pt = (new_pt[0][0], new_pt[1][0], new_pt[2][0])
            new_pts.append(pt)
            new_h_pts.append(new_h_pt)
        new_pts = np.array(new_pts)
        h_pts = new_h_pts

        return new_pts


    ### ------------------------------------------------------------------
### This is your main function and is called when the extension is run.
    
    def effect(self):
        # Just for 'fun' - report Python version
        
        # check for correct number of selected objects and return a translatable errormessage to the user
        # if len(self.options.ids) >= 1:
        #     inkex.errormsg(("This extension requires at least 1 selected path."))
        #     exit()

        # gather incoming params and convert
        mm_conv = self.uutounit(1.0, 'mm')
        #inkex.debug('mm_conv='+ str(mm_conv))
        in_to_mm = 25.4


        thread_offset = self.options.thread_offset * in_to_mm
        zigzag = self.options.zigzag

        r1x = self.options.r1x * in_to_mm
        r1y = self.options.r1y * in_to_mm
        r2x = self.options.r2x * in_to_mm
        r2y = self.options.r2y * in_to_mm

        filename = self.options.filename
        path = self.options.dir
        debug = self.options.debug
        overwrite = self.options.overwrite



        temp = str(r1x) + str(r1y)  + str(r2x)   + str(r2y)
        #inkex.debug(debug)
        #inkex.debug(dir)

        # what page are we on
        page_id = self.options.active_tab # sometimes wrong the very first time

        #get the path points
        #from extrude.py
        paths = []
        for id, node in self.selected.iteritems():
            if node.tag == '{http://www.w3.org/2000/svg}path':
                paths.append(node)

        pts = [cubicsuperpath.parsePath(paths[i].get('d'))
               for i in range(len(paths))]

        for i in range(len(paths)):
            if 'transform' in paths[i].keys():
                trans = paths[i].get('transform')
                trans = simpletransform.parseTransform(trans)
                simpletransform.applyTransformToPath(trans, pts[i])

        #at this point, pts is our list of points, but it is embedded in lots of brackets.
        #so convert to list of x,y pairs
        #all points in mm!
        pts = np.array(pts)* mm_conv
        pts = pts.flatten()
        pts = zip(pts[::2], -pts[1::2])

        #here we need to check the registration points and do our transformation...
        ink_r1 = self.get_registration('R1','R1_a')
        ink_r2 = self.get_registration('R2','R2_a')

        #inkscape y values are negative
        ink_r1 = (ink_r1[0], -ink_r1[1])
        ink_r2 = (ink_r2[0], -ink_r2[1])

        #convert to mm
        ink_r1 = (np.array(ink_r1) * mm_conv).tolist()
        ink_r2 = (np.array(ink_r2) * mm_conv).tolist()

        tempstr = 'thread_offset = ' + str(thread_offset)
        if debug == 'true':
            inkex.debug(tempstr)

        tempstr = 'r1_ink = ' + str(ink_r1)
        if debug == 'true':
            inkex.debug(tempstr)

        tempstr = 'r2_ink = ' + str(ink_r2)
        if debug == 'true':
            inkex.debug(tempstr)

        tempstr = 'r1_emb = ' + str([r1x, r1y])
        if debug == 'true':
            inkex.debug(tempstr)

        tempstr = 'r2_emb = ' + str([r2x, r2y])
        if debug == 'true':
            inkex.debug(tempstr)

        tempstr = 'pts = ' + str(pts)
        if debug == 'true':
            inkex.debug(tempstr)

        #we have all the variables now to process the path
        # pts = all the points in the path
        # thread_offset = thread offset for the zigzag
        r1_ink = ink_r1
        r2_ink = ink_r2
        r1_emb = [r1x, r1y]
        r2_emb = [r2x, r2y]

        if pts == []:
            inkex.debug(' **** YOU HAVE TO CHOOSE A PATH ****')
        else:


            #this fuction takes pts and makes new_pts by scaling,translating and rotating based upon the reg points
            new_pts = self.get_translated_points(pts, r1_ink, r2_ink, r1_emb, r2_emb)
            #normalize points adds or removes points so that the diff between one point and the next is between 10 and 14mm
            new_pts = normalize_pts(new_pts, 1, 4)
            #zigzag them if needed
            if zigzag == 'true':
                new_pts = getzigzag(new_pts)

            #debug the new points
            debug_new_points = []
            for pt in new_pts:
                debug_new_points.append((pt[0],pt[1]))
            tempstr = 'new_pts = ' + str(debug_new_points)
            if debug == 'true':
                inkex.debug(tempstr)

            r1_ink = np.array(r1_ink)
            r2_ink = np.array(r2_ink)
            r1_emb = np.array(r1_emb)
            r2_emb = np.array(r2_emb)
            pts = np.array(pts)
            new_pts = np.array(new_pts)

            #make a pes file
            if self.validate_path():
                if overwrite == 'true':
                    result = make_pes(path, filename, new_pts, False)
                    tempstr = '# saved to: ' + path + filename
                elif not os.path.isfile(path + filename):
                    result = make_pes(path, filename, new_pts, False)
                    tempstr = '# saved to: ' + path + filename
                else:
                    tempstr = '# ' + path + filename + ' not saved!  Is overwrite set?'
                if debug == 'true':
                    inkex.debug(tempstr)

        return

if __name__ == '__main__':
    e = Embroider()
    e.affect()



