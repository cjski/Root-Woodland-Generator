from WoodlandCommon import *
import numpy as np

class Path:
    def __init__( self, clearing1, clearing2 ):
        self.clearing1 = clearing1
        self.clearing2 = clearing2
  
    # Given three collinear points p, q, r, the function checks if 
    # point q lies on line segment 'pr' 
    def onSegment(self, p, q, r):
        if ( (q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and 
               (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
            return True
        return False
  
    def orientation(self, p, q, r):
        # to find the orientation of an ordered triplet (p,q,r)
        # function returns the following values:
        # 0 : Collinear points
        # 1 : Clockwise points
        # 2 : Counterclockwise
          
        val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))
        if (val > 0):
              
            # Clockwise orientation
            return 1
        elif (val < 0):
              
            # Counterclockwise orientation
            return 2
        else:
              
            # Collinear orientation
            return 0
      
    # The main function that returns true if 
    # the line segment 'p1q1' and 'p2q2' intersect.
    def intersects( self, p2, q2):
        p1 = self.clearing1.pos
        q1 = self.clearing2.pos

        # If any of these lines start at the same point we can ignore this
        if ( np.array_equal( p1, p2 ) or
             np.array_equal( p1, q2 ) or
             np.array_equal( q1, p2 )or
             np.array_equal( q1, q2 ) ):
            return False
        
        # Find the 4 orientations required for 
        # the general and special cases
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)
      
        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True
      
        # Special Cases
      
        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        if ((o1 == 0) and self.onSegment(p1, p2, q1)):
            return True
      
        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        if ((o2 == 0) and self.onSegment(p1, q2, q1)):
            return True
      
        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        if ((o3 == 0) and self.onSegment(p2, p1, q2)):
            return True
      
        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
        if ((o4 == 0) and self.onSegment(p2, q1, q2)):
            return True
      
        # If none of the cases
        return False

