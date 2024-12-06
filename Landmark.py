from WoodlandCommon import *

import pygame
from enum import Enum
import numpy as np

class Landmark:
    size = 0
    outlineWidth = 1
    def __init__( self, pos ):
        self.pos = pos
        self.name = ""

    def draw( self, screen ):
        return

    def drawName( self, screen ):
        nameTextSize = font18.size( self.name )
        nameTextPos = [ self.pos[0] - nameTextSize[0] / 2.0, self.pos[1] + self.size / 2.0 ]
        outlineText( screen, nameTextPos, self.name, font18, WHITE, BLACK )


class LandmarkType(Enum):
    RUIN = 0
    GREATTREE = 1
    SHIPWRECK = 2
    CAVE = 3
    VOLCANO = 4
    BEAR = 5
    ELK = 6
    SHRINE = 7
    

class Ruin(Landmark):
    size = 30
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Ruins"

    def draw( self, screen ):
        ruin1Points = [ [-.6, .5], [-.6, .1], [-.4, .1], [-.4, .5] ]
        ruin2Points = [ [-.3, .5], [-.3, -.1], [-.2, -.1], [-.2, 0.0], [-.1, 0.0], [-.1, -.4], [.2, -.4], [.2, .5] ]
        ruin3Points = [ [.3, .5], [.3, -.1], [.45, -.1], [.45, .2], [.6, .2], [.6, .5] ]
        grassPoints = [ [-.65, .5], [-.5, .3], [-.4, .45], [-.3, .3], [-.2, .45], [-.1, .3], [0.0, .45], [.1, .3], [.2, .45], [.3, .3], [.4, .45], [.5, .3], [.65, .5] ]

        colours = [ GREY, GREY, GREY, DARK_GREEN ]
        allRuins = [ ruin1Points, ruin2Points, ruin3Points, grassPoints ]

        for pointsIndex in range( len( allRuins ) ):
            ruinPoints = allRuins[pointsIndex]
            for i in range( len( ruinPoints ) ):
                ruinPoints[i] = self.pos + self.size * np.array( ruinPoints[i] )

            pygame.draw.polygon( screen, colours[pointsIndex], ruinPoints )
            pygame.draw.polygon( screen, BLACK, ruinPoints, width=self.outlineWidth )
            
        self.drawName( screen )


class GreatTree(Landmark):
    size = 40
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Great Tree"

    def draw( self, screen ):
        barkPoints = [ [-.3, .5], [-.2, .425], [-.2, -.3], [.2, -.3], [.2, .425], [.3, .5] ]

        for i in range( len( barkPoints ) ):
            barkPoints[i] = self.pos + self.size * np.array( barkPoints[i] )

        pygame.draw.polygon( screen, BROWN, barkPoints )
        pygame.draw.polygon( screen, BLACK, barkPoints, width=self.outlineWidth )
        
        leavesPoints = [ [-.2, -.1], [.2, -.1], [-.4, -.35], [.4, -.35], [0, -.45] ]
        leavesRadii = [ .2, .2, .3, .3, .4 ]
        for i in range( len( leavesPoints ) ):
            actualRad = self.size * leavesRadii[i]
            actualPos = self.pos + self.size * np.array( leavesPoints[i] )
            pygame.draw.circle( screen, DARK_GREEN, actualPos, actualRad )
            pygame.draw.circle( screen, BLACK, actualPos, actualRad, width=self.outlineWidth )
            
        self.drawName( screen )


class Shipwreck(Landmark):
    size = 30
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Shipwreck"

    def draw( self, screen ):
        shipwreckPoints = [ [-.25, .5], [.15, .1], [.2, .15], [.1, .25], [.125, .275], [.2, .5] ]

        for i in range( len( shipwreckPoints ) ):
            shipwreckPoints[i] = self.pos + self.size * np.array( shipwreckPoints[i] )

        pygame.draw.polygon( screen, BROWN, shipwreckPoints )
        pygame.draw.polygon( screen, BLACK, shipwreckPoints, width=self.outlineWidth )

        waterPoints = [ [-.35, .5], [-.225, .45], [-.1, .475], [0.0, .45], [.1, .475], [0.225, .45], [.35, .5] ]

        for i in range( len( waterPoints ) ):
            waterPoints[i] = self.pos + self.size * np.array( waterPoints[i] )

        pygame.draw.polygon( screen, LIGHT_BLUE, waterPoints )
        pygame.draw.lines( screen, BLACK, False, waterPoints, width=self.outlineWidth )
            
        self.drawName( screen )


class Cave(Landmark):
    size = 40
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Old Mine"

    def draw( self, screen ):
        cave1Points = [ [-.6, .5], [-.45, .4], [-.4, .15], [-.2, .11], [-.05, -.1], [.15, -.05], [.3, 0.0], [.4, .2], [.5, .2], [.5, .4], [.6, .5] ]
        cave2Points = [ [-.25, .5], [-.25, .3], [-.1, .15], [.1, .15], [.25, .3], [.25, .5] ]
        strut1Points = [ [-.175, .5], [-.175, .26], [-.15, .235], [-.15, .5] ]
        strut2Points = [ [.175, .5], [.175, .26], [.15, 0.235 ], [.15, .5] ]

        colours = [ LIGHT_GREY, BLACK, BROWN, BROWN ]
        allCaves = [ cave1Points, cave2Points, strut1Points, strut2Points ]

        for pointsIndex in range( len( allCaves ) ):
            points = allCaves[pointsIndex]
            for i in range( len( points ) ):
                points[i] = self.pos + self.size * np.array( points[i] )

            pygame.draw.polygon( screen, colours[pointsIndex], points )

        pygame.draw.polygon( screen, BLACK, cave1Points, width=self.outlineWidth ) 
            
        self.drawName( screen )
        

class Volcano(Landmark):
    size = 60
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Fiery Mountain"

    def draw( self, screen ):
        smokePoints = [ [-.02, -.2], [.02, -.2], [-.02, -.3], [.02, -.3], [0, -.4], [0.05, -.45], [0.1, -.375], [.2, -.4] ]
        smokeRad = 0.1
        actualRad = self.size * smokeRad
        for i in range( len( smokePoints ) ):
            actualPos = self.pos + self.size * np.array( smokePoints[i] )
            pygame.draw.circle( screen, BLACK, actualPos, actualRad )
        
        mountainPoints = [ [-.5, .5], [-.4, .3], [-.3, .4], [-.15, -.2], [.15, -.2], [.3, .4], [.45, .35], [.5, .5] ]
        
        colours = [ GREY ]
        allPoints = [ mountainPoints ]

        for pointsIndex in range( len( allPoints ) ):
            points = allPoints[pointsIndex]
            for i in range( len( points ) ):
                points[i] = self.pos + self.size * np.array( points[i] )

            pygame.draw.polygon( screen, colours[pointsIndex], points )

        pygame.draw.polygon( screen, BLACK, mountainPoints, width=self.outlineWidth )

        lavaPoints = [ [-.15, -.2], [.15, -.2] ]
        for i in range( len( lavaPoints ) ):
            lavaPoints[i] = self.pos + self.size * np.array( lavaPoints[i] )
                
        pygame.draw.lines( screen, ORANGE, False, lavaPoints, width=self.outlineWidth * 2 )
            
        self.drawName( screen )


class Bear(Landmark):
    size = 40
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Bear"

    def draw( self, screen ):
        points = [ [.4, .5], [-.25, .5], [-.15, .2], [-.2, .2], [-.25, .15], [-.25, .125], [-.22, .09], [-.19, .125],
                   [-.16, .09], [-.13, .125], [-.1, .09], [-.07, .125], [-.07, 0.0], [-.1, .035], [-.13, .0],
                   [-.16, .035], [-.19, .0], [-.23, .035], [-.25, .0], [-.265, -.125], [-.225, -.125], [-.225, -.1],
                   [-.075, -.2], [.025, -.2], [.035, -.25], [.05, -.265], [.15, -.26], [.175, -.235], [.2, -.15], [.3, -.05],
                   [.35, .2] ]
        
        for i in range( len( points ) ):
            points[i] = self.pos + self.size * np.array( points[i] )
            
        pygame.draw.polygon( screen, BROWN, points )        
        pygame.draw.polygon( screen, BLACK, points, width=self.outlineWidth )
        self.drawName( screen )


class Elk(Landmark):
    size = 40
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Sage"

    def draw( self, screen ):
        points = [ [-.2, .5], [-.1, .2], [-.125, .1], [-.35, .05], [-.375, .0], [.0, -.2],
                   [-.25, -.225], [-.3, -.35], [-.225, -.275], [0.05, -.25], [0.125, -.25], [0.15, -.325], [-.05, -.4], [0.16, -.375],
                   [0.175, -.45], [.1, -.6], [0.225, -.475], [0.1825, -.2825], [0.3, -.4], [.225, -.25], [.15, -.2],
                   [.3, -.175], [.2, -.1], [.25, .5] ]
        
        for i in range( len( points ) ):
            points[i] = self.pos + self.size * np.array( points[i] )
            
        pygame.draw.polygon( screen, BROWN, points )        
        pygame.draw.polygon( screen, BLACK, points, width=self.outlineWidth )
        self.drawName( screen )


class Shrine(Landmark):
    size = 40
    def __init__( self, pos ):
        super().__init__( pos )
        self.name = "Shrine"

    def draw( self, screen ):
        shrineStep1Points = [ [-.4, .5], [-.4, .4], [.4, .4], [.4, .5] ]
        shrineStep2Points = [ [-.3, .4], [-.3, .3], [.3, .3], [.3, .4] ]
        shrinePoints = [ [-.225, .3], [-.225, .0], [.0, -.225], [.225, .0], [.225, .3] ]
        shrineRoofPoints = [ [.0, -.225], [.25, .05], [.3, .0], [.0, -.3], [-.3, .0], [-.25, .05] ]
        shrineBoxPoints = [ [-.15, .225], [-.15, .075], [.0, -.125], [.15, .075], [.15, .225] ]

        colours = [ GREY, GREY, LIGHT_BROWN, BROWN, BROWN ]
        allPoints = [ shrineStep1Points, shrineStep2Points, shrinePoints, shrineRoofPoints, shrineBoxPoints ]

        for pointsIndex in range( len( allPoints ) ):
            points = allPoints[pointsIndex]
            for i in range( len( points ) ):
                points[i] = self.pos + self.size * np.array( points[i] )

            pygame.draw.polygon( screen, colours[pointsIndex], points )
            pygame.draw.polygon( screen, BLACK, points, width=self.outlineWidth )
            
        self.drawName( screen )
