#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 15:42:52 2017

@author: gjacopo
"""

from __future__ import print_function

import warnings
from collections import OrderedDict

import math
import random

try:
    import numpy as np
except:
    raise IOError("Package numpy not imported - Requested")
    
try:
    import pandas as pd
    PDVERS = int(pd.__version__.split('.')[1])
except:
    PDVERS = 0 # unknown
    raise IOError("Package pandas not imported - Requested")

#from matplotlib import pyplot as plt
 
class PackedCircles(object):
    
    # tuple indices
    X, Y, RADIUS = 0, 1, 2
    # after sorting the radii in descending order by size, the list is split along 
    # SORT_PARAM_1 and the second piece is randomized. The pieces are then added 
    # back together and the list is split along SORT_PARAM_2 and the first piece is
    # shuffled. The lists are then added together and returned. 
    SORT_PARAM_1, SORT_PARAM_2 = .0, .10
    # examples: (1, 0) = totally sorted - appealing border, dense center, sparse midradius
    #           (0, 1), (1, 1) = totally randomized - packed center, ragged border
    # these constants control how close points are placed w.r.t. each other
    RADIAL_RESOLUTION, ANGULAR_RESOLUTION = .4, .4 
    # this keeps the boundaries from touching
    PADDING = 0
    
    @classmethod
    def distance(cls, p0, p1):
        return math.sqrt((p0[cls.X] - p1[cls.X])**2 + (p0[cls.Y] - p1[cls.Y])**2)
        
    def __init__(self, **kwargs):
        self.__rad = []
        self.__pos = []
        self.__circles = []
        if kwargs == {}:
            return
        attrs = ('rad','circles','pos') 
        for attr in list(set(attrs).intersection(kwargs.keys())):
            try:
                setattr(self, '{}'.format(attr), kwargs.pop(attr))
            except: 
                warnings.warn('wrong attribute value {}'.format(attr.upper()))
         
    @property
    def rad(self):
        return self.__rad
    @rad.setter
    def rad(self, rad):
        self.__rad = rad
    @property
    def pos(self):
        return self.__pos
    @pos.setter
    def pos(self, pos):
        self.__pos = pos
    @property
    def circles(self):
        return self.__circles
    @circles.setter
    def circles(self, circles):
        self.__circles = circles

    def plot(self):
        try:
            import pylab
            from colorsys import hsv_to_rgb
            from matplotlib.patches import Circle
        except:
            raise IOError("missing plot module")
        # each circle is a tuple of the form (x, y, r)
        circles = self.circles
        pylab.figure()
        bx = pylab.gca()
        rs = [x[2] for x in circles]
        maxr, minr = max(rs), min(rs)
        hue = lambda inc: pow(float(inc - minr)/(1.02*(maxr - minr)), 3)
        for circle in circles:
            circ = Circle((circle[0], circle[1]), circle[2])
            color = hsv_to_rgb(hue(circle[2]), 1, 1)
            circ.set_color(color); circ.set_edgecolor(color)
            bx.add_patch(circ)
        pylab.axis('scaled')
        pylab.show()

    def position(self, rand=False, order=None):

        if rand is True:
            # positions the circles randomly
            maxr = int(max(self.rad)/2)
            numc = len(self.rad)
            scale = int(pow(numc, 0.5))
            maxr = scale*maxr
            circles = [(random.randint(-maxr, maxr), random.randint(-maxr, maxr), r)
                       for r in self.rad]
        else:
            points = self._base_points(PackedCircles.ANGULAR_RESOLUTION, PackedCircles.RADIAL_RESOLUTION)
            free_points = []
            radii = self._fix_radii(self.rad, order=order)
         
            circles = []
            point_count = 0
            for radius in radii:
                #if radius ==0.0:
                #    continue
                i, L = 0, len(free_points)
                print ("{0} free points available, {1} circles placed, {2} points examined".format(L, len(circles), point_count))
                while i < L:
                    if self._available(circles, free_points[i], radius):
                        self.make_circle(free_points.pop(i), radius, circles, free_points)
                        break  
                    else:
                        i += 1  
                else:
                    for point in points:
                        point_count += 1
                        if self._available(circles, point, radius):
                            self.make_circle(point, radius, circles, free_points)
                            break
                        else:
                            if not self._contained(circles, point):
                                free_points.append(point)
        self.__circles = self._check(circles)
        #return 

    @staticmethod
    def _check(circles):
        intersections = 0
        for c1 in circles:
            for c2 in circles:
                if c1 is not c2 and PackedCircles.distance(c1, c2) < c1[PackedCircles.RADIUS] + c2[PackedCircles.RADIUS]:
                    intersections += 1
                    break
        # print ("{0} intersections".format(intersections))
        if intersections:
            raise AssertionError('intersections!')
        return circles

    @staticmethod
    def _fix_radii(radii, order=None):
        if order is None:
            radii = sorted(radii, reverse=True)
        else:
            radii = radii[order]
        radii_len = len(radii)
     
        section1_index = int(radii_len * PackedCircles.SORT_PARAM_1)
        section2_index = int(radii_len * PackedCircles.SORT_PARAM_2)
     
        section1, section2 = radii[:section1_index], radii[section1_index:]
        random.shuffle(section2)
        radii = section1 + section2
     
        section1, section2 = radii[:section2_index], radii[section2_index:]
        random.shuffle(section1)
        return section1 + section2
     
    def make_circle(self, point, radius, circles, free_points):
        new_circle = point + (radius, )
        circles.append(new_circle)
        i = len(free_points) - 1
        while i >= 0:
            if self._contains(new_circle, free_points[i]):
                free_points.pop(i)
            i -= 1
                       
    @staticmethod
    def _available(circles, point, radius):
        for circle in circles:
            if PackedCircles.distance(point, circle) < radius + circle[PackedCircles.RADIUS] + PackedCircles.PADDING:
                return False
        return True
           
    @staticmethod     
    def _base_points(radial_res, angular_res):
        circle_angle = 2 * math.pi
        r = 0
        while 1:
            theta = 0
            while theta <= circle_angle:
                yield (r * math.cos(theta), r * math.sin(theta))
                r_ = math.sqrt(r) if r > 1 else 1
                theta += angular_res/r_
            r += radial_res    
          
    @staticmethod
    def _contains(circle, point):
        return PackedCircles.distance(circle, point) < circle[PackedCircles.RADIUS] + PackedCircles.PADDING
     
    @staticmethod
    def _contained(circles, point):
        return any(PackedCircles.distance(c, point) < c[PackedCircles.RADIUS] + PackedCircles.PADDING \
                   for c in circles)

class ChartWindow(object):
    
    SHIFT       = 100
    
    WIDTH       = 970
    HEIGHT      = 850 # 2000 
    COLS        = [  4,   4,   4,    4,    4,    4,    4,    4] # say that 4 is the max we accept on a row (by default)
    ROWPADD     = [100, 100, 100,  100,  100,  100,  100,  100]
    ROWPOS      = [450, 650, 850, 1050, 1250, 1450, 1650, 1850] 
    ROWOFF      = [80,   80,  80,   80,   80,   80,   80,   80]
    COLOFF      = [50,   50,  50,   50,   50,   50,   50,   50]

    DOMAIN      = [0, 600]
    RRANGE       = [1, 90]

    CENTERX     = WIDTH / 2
    CENTERY     = 300
    
    MAXRAD      = 200
    
    def rScale(self, x):
        # equivalent of d3.scale.pow().exponent(0.5).domain(DOMAIN).range(RRANGE),
        a = (self.rrange[1] - self.rrange[0]) / np.sqrt(self.domain[1] - self.domain[0])
        b = self.rrange[0] - a * np.sqrt(self.domain[0])
        return a * np.sqrt(np.abs(x)) + b

    def __init__(self, **kwargs):
        self.width, self.height = ChartWindow.WIDTH, ChartWindow.HEIGHT
        self.cols = ChartWindow.COLS
        self.rowPadd = ChartWindow.ROWPADD
        self.rowPos = ChartWindow.ROWPOS 
        self.rowOff = ChartWindow.ROWOFF
        self.colOff = ChartWindow.COLOFF
        self.domain = ChartWindow.DOMAIN
        self.rrange = ChartWindow.RRANGE
        self.centerX, self.centerY = None, None
        if kwargs == {}:
            return
        attrs = ('width','height','cols','rowPadd','rowPos','rowOff',
                 'domain','rrange','centerX','centerY') 
        for attr in list(set(attrs).intersection(kwargs.keys())):
            try:
                setattr(self, '{}'.format(attr), kwargs.pop(attr))
            except: 
                warnings.warn('wrong attribute value {}'.format(attr.upper()))
        if self.centerX is None: 
            self.centerX = self.width/2
        if self.centerY is None:    
            self.centerY = self.height/2 - ChartWindow.SHIFT
        m = min([len(getattr(self, '{}'.format(attr)))                  \
                             for attr in ['cols','rowPadd','rowPos','rowOff','colOff']])
        for attr in ['cols', 'rowPadd', 'rowPos', 'rowOff', 'colOff']:
            try:
                setattr(self, '{}'.format(attr), getattr(self, '{}'.format(attr))[:m])
            except: 
                pass
            
    def table_cells(self, iList):
        posLookup = OrderedDict({})
        if iList == (): return posLookup
        for i, item in enumerate(iList):
            if item in posLookup: continue # that does the trick for quincunx_cells
            t = 0
            numInRow, posInRow, curRow = -1, -1, -1
            for j in range (len(self.cols)):
                if i < (t + self.cols[j]):
                    numInRow = self.cols[j]
                    posInRow, curRow = i - t, j
                    break
                t += self.cols[j]
            if numInRow == -1:
                numInRow = len(iList) - sum(self.cols)
                curRow = len(self.cols)
                posInRow = i  - sum(self.cols)
            w = (self.width - 2*self.rowPadd[curRow]) / (numInRow-1)
            currentX = w * posInRow + self.rowPadd[curRow]
            currentY = self.rowPos[curRow]
            posLookup[item] = {'row': curRow, 
                                'x': int(currentX), 
                                'y': int(currentY) - (ChartWindow.SHIFT/2),
                                'offy': self.rowOff[curRow], 
                                'offx': 0 # self.colOff[curRow] 
                                }           
        return posLookup
        
    def quincunx_cells(self, iList):
        iList = [x for t in zip(iList, iList) for x in t]
        posLookup = self.table_cells(iList)     
        for item in posLookup:
            posLookup[item].update({'x':posLookup[item]['x']                        \
                                    + (posLookup[item]['row']%2)*ChartWindow.SHIFT, \
                                    'offx': self.colOff[posLookup[item]['row']] + (ChartWindow.SHIFT/2),    \
                                    'y': posLookup[item]['y'] + (ChartWindow.SHIFT/2)})
        return posLookup
        
    def circle_segments(self, iDict):
        posLookup = OrderedDict({})
        if iDict == {}:     return posLookup
        # else:               N = len(iList)
        items, mass = iDict.keys(), iDict.values()
        iM = np.array(list(mass)) / sum(list(mass))
        rad = max(min(self.width/2,self.height/2) - 300, ChartWindow.MAXRAD)
        for item, a in zip(items, [(2 * p - 1.) * math.pi for p in iM.cumsum()]):
            posLookup[item] = { 'x': int(self.centerX + rad*math.cos(a)), \
                                'y': int(self.centerY + ChartWindow.SHIFT + rad*math.sin(a))} 
        return posLookup
        
