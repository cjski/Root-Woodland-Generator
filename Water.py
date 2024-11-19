from WoodlandCommon import *

import numpy as np
import random
import math

class Water:
    # These are the expected values for 12 clearings. Above that it'll be scaled
    maxLakeClearings = 5
    minLakeClearings = 3
    maxDestroyablePaths = 2
    
    minAuxPoints = 3
    maxAuxPoints = 10
    auxPointsVariance = 20
    fromClearingBuffer = 4
    farClearingBufferMin = 5
    farClearingBufferMax = 10
    lakeEdgeAddChance = 0.6
    smoothingRefinements = 5
    minCoastPoints = 2
    maxCoastPoints = 8
    
    def __init__( self, triangles, riverPoints, woodland ):
        self.triangles = triangles
        self.riverPoints = riverPoints
        self.hull = []
        self.woodland = woodland
        self.generateHull()
    
    def generateHull( self ):
        dt = self.woodland.tri
        clearings = self.woodland.clearings
        numClearings = len(clearings)

        # If we have a lake made of triangles draw that and the river
        if len( self.triangles ) > 0:
            # Any edge thats only in the set once is on the edge of the hull. Search the edges and then construct the hull by matching which ones connect
            numPoints = len( dt.points )
            edges = [ [ 0 for i in range( numPoints ) ] for j in range( numPoints ) ]
            # First point is just going to be the lowest indexed point
            firstPoint = numPoints
            for triangle in self.triangles:
                simplices = dt.simplices[triangle]
                edge1 = ( simplices[0], simplices[1] )
                edge2 = ( simplices[0], simplices[2] )
                edge3 = ( simplices[1], simplices[2] )
                triEdges = [edge1, edge2, edge3]

                for edge in triEdges:
                    edges[edge[0]][edge[1]] += 1
                    edges[edge[1]][edge[0]] += 1

                lowestPoint = min( simplices )
                if ( lowestPoint < firstPoint ):
                    firstPoint = lowestPoint

            pointIndexes = [ firstPoint ]
            visited = [False for i in range(numPoints)]
            visited[ firstPoint ] = True
            
            currPoint = firstPoint
            done = False
            
            # Find the order of the points
            while ( not done ):
                nextPoint = -1
                for i in range( numPoints ):
                    if ( edges[currPoint][i] == 1 and not visited[i] ):
                        nextPoint = i
                        break
                
                # Done the loop, end
                if ( nextPoint == -1 ):
                    done = True
                else:
                    visited[nextPoint] = True
                    pointIndexes.append(nextPoint)
                    currPoint = nextPoint

            leftMostIndex = 0
            for i in range( 1, len( pointIndexes ) ):
                if ( dt.points[pointIndexes[i]][0] < dt.points[pointIndexes[leftMostIndex]][0] ):
                    leftMostIndex = i
            
            leftMost = pointIndexes[leftMostIndex]
            nextPoint = pointIndexes[0] if ( leftMostIndex + 1 >= len( pointIndexes ) ) else pointIndexes[leftMostIndex+1]
            prevPoint = pointIndexes[-1] if ( leftMostIndex - 1 < 0 ) else pointIndexes[leftMostIndex-1]

            toLeftMost = dt.points[leftMost] - dt.points[prevPoint]
            toNext = dt.points[nextPoint] - dt.points[leftMost]

            # Determinant of ( [ a b ] [ c d ] ) = ad - bc
            # If det > 0 CCW else CW
            # ab -> toLeftMost  cd -> toRightMost
            direction = toLeftMost[0] * toNext[1] - toLeftMost[1] * toNext[0]

            self.hull = []
            # Biasing the point away from the clearing
            for i in range(len(pointIndexes)):
                curr = pointIndexes[i]
                nextPoint = pointIndexes[0] if ( i + 1 >= len( pointIndexes ) ) else pointIndexes[i+1]
                prevPoint = pointIndexes[-1] if ( i - 1 < 0 ) else pointIndexes[i-1]

                if ( curr < numClearings ):
                    clearing = clearings[curr]
                    # If this point is connected to the river, don't add coast points, just attach the river to it
                    if ( clearing.hasFeature( "River" ) ):
                        # Going CW so we're approaching the left side and the order of points in the river is right
                        if direction < 0:
                            self.hull += self.riverPoints
                        # Going CCW, so we're approaching the right side, we need to reverse this list of points
                        else:
                            self.hull += self.riverPoints[::-1]
                    else:    
                        angleToNext = math.atan2( dt.points[nextPoint][1] - dt.points[curr][1], dt.points[nextPoint][0] - dt.points[curr][0] )
                        angleToPrev = math.atan2( dt.points[prevPoint][1] - dt.points[curr][1], dt.points[prevPoint][0] - dt.points[curr][0] )

                        startAngle = 0
                        endAngle = 0
                        angleDelta = 0
                        # Going CW
                        if direction < 0:
                            startAngle = angleToPrev
                            endAngle = angleToNext
                        # Going CCW
                        else:
                            startAngle = angleToNext
                            endAngle = angleToPrev

                        if endAngle < startAngle:
                            endAngle += 2 * math.pi
                        
                        angleDelta = endAngle - startAngle
                        coastPoints = []

                        numCoastPoints = self.minCoastPoints + int( ( self.maxCoastPoints - self.minCoastPoints ) * angleDelta / ( 2 * math.pi ) )
                        
                        for cIndex in range( numCoastPoints ):
                            angle = startAngle + cIndex * angleDelta / float( numCoastPoints - 1 )
                            rot = np.array([[ math.cos(angle), -math.sin(angle) ], [ math.sin(angle), math.cos(angle) ]])
                            point = clearing.pos + ( clearing.rad + self.fromClearingBuffer ) * np.dot( rot, np.array( [1, 0] ) )
                            coastPoints.append( point )

                        # Going CCW, need to flip this order
                        if direction > 0:
                            coastPoints.reverse()

                        self.hull += coastPoints
                # If not a clearing just add in the last point
                else:
                    self.hull += [dt.points[curr]]

                # Make the outline more complex

                # Scale the line so we don't hit the center of the next clearing
                toNext = ( dt.points[nextPoint] - self.hull[-1] )
                toNextLen = np.linalg.norm(toNext)
                right = np.array([ toNext[1], -toNext[0] ]) / toNextLen

                # We need a buffer if we're going to be going into another clearing so we don't draw past the coast points
                fromPointBuffer = 0
                if ( curr < numClearings ):
                    clearing = clearings[curr]
                    fromPointBuffer += clearing.rad + self.fromClearingBuffer + self.farClearingBufferMax
    
                numAuxPoints = self.minAuxPoints + int( ( self.maxAuxPoints - self.minAuxPoints ) * toNextLen / self.woodland.size[0] )
                toNext = toNext * ( toNextLen - fromPointBuffer ) / toNextLen
                
                fakeEndPoint = self.hull[-1] + toNext
                toNext = toNext / ( numAuxPoints + 1 )
                auxPointStart = len(self.hull)
                for aux in range( numAuxPoints ):
                    auxPoint = self.hull[-1] + toNext
                    self.hull.append(auxPoint)

                firstBufferedPoint = -1
                lastBufferedPoint = -1

                # Add some randomness and fix points too close to settlements
                for aux in range( auxPointStart, auxPointStart + numAuxPoints ):
                    curAuxPoint = self.hull[aux]
                    curAuxPoint += right * random.uniform(-self.auxPointsVariance, self.auxPointsVariance)
                    
                    isBuffer = False
                    # Push the point away from clearings its too close to
                    for awayClearing in clearings:
                        if curr < numClearings and clearings[curr] != awayClearing:
                            minFarClearingDist = awayClearing.rad + self.fromClearingBuffer + self.farClearingBufferMin
                            currDist = np.linalg.norm( curAuxPoint - awayClearing.pos )
                            if currDist < minFarClearingDist:
                                isBuffer = True
                                # Scale the point in between the ranges
                                maxFarClearingDist = awayClearing.rad + self.fromClearingBuffer + self.farClearingBufferMax
                                # The distance to add to this point
                                bufferDist = np.random.uniform(low=minFarClearingDist, high=maxFarClearingDist)
                                newPoint = curAuxPoint + ( bufferDist / currDist )*( curAuxPoint - awayClearing.pos )
                                self.hull[aux] = newPoint

                    if isBuffer:
                        # We need to know when the points were buffered so we can clean the rest of the ones before and after them
                        if firstBufferedPoint == -1:
                            firstBufferedPoint = aux
                        else:
                            lastBufferedPoint = aux

                if firstBufferedPoint != -1 and lastBufferedPoint == -1:
                    lastBufferedPoint = len(self.hull) - 1

                if firstBufferedPoint != -1:
                    # Clean up the points before and after the buffer
                    startFixUp = max(auxPointStart, 0)
                    endFixUp = len(self.hull)
                    startVec = (self.hull[firstBufferedPoint] - self.hull[startFixUp])/(max(firstBufferedPoint - startFixUp,1))
                    endVec = (fakeEndPoint - self.hull[lastBufferedPoint])/(max(endFixUp - lastBufferedPoint,1))
                    
                    for i in range(startFixUp, firstBufferedPoint):
                        newPoint = self.hull[startFixUp] + startVec * (i - startFixUp)
                        newPoint += right * random.uniform(-self.auxPointsVariance, self.auxPointsVariance)
                        self.hull[i] = newPoint

                    for i in range(lastBufferedPoint+1, endFixUp):
                        newPoint = self.hull[lastBufferedPoint] + endVec * (i - lastBufferedPoint)
                        newPoint += right * random.uniform(-self.auxPointsVariance, self.auxPointsVariance)
                        self.hull[i] = newPoint


        # If we just have a river make that the hull
        else:
            self.hull = self.riverPoints

            # Add a few points to the front and end of the river so that it goes over the edge and doesnt get visibly smoothed down by the refining
            back1 = self.riverPoints[0] - self.riverPoints[1]
            back2 = self.riverPoints[-1] - self.riverPoints[-2]

            self.hull.append( self.riverPoints[-1] + back2 )
            self.hull.append( self.riverPoints[0] + back1 )

        # Smooth our water down  
        self.hull = self.smoothCorners( self.hull, self.smoothingRefinements )

        
    def smoothCorners( self, points, refinements ):
        points = np.array(points)
        
        for i in range(refinements):
            L = points.repeat(2, axis=0)
            R = np.empty_like(L)
            R[0] = L[-1]
            R[2::2] = L[1:-1:2]
            R[1:-1:2] = L[2::2]
            R[-1] = L[0]
            points = L * 0.80 + R * 0.20

        return points.tolist()

    # Greater than 0 is CCW, Less is CW, equal is colinear
    def det( self, p1, p2, p3 ):
        return ( p2[0] - p1[0] ) * ( p3[1] - p1[1] ) - ( p2[1] - p1[1] ) * ( p3[0] - p1[0] )
        
    def draw( self, screen ):
        pygame.draw.polygon( screen, LIGHT_BLUE, self.hull )

