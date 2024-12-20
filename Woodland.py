from WoodlandCommon import *
from Path import *
from Clearing import *
from Water import *
from Landmark import *

from enum import Enum
import pygame
import random
import math
import numpy as np
from scipy.spatial import Delaunay
from scipy import interpolate as intp

class DTType(Enum):
    FOREST = 0
    LAKE = 1
    MOUNTAIN = 2
    MARSH = 3


class Woodland:
    # Below this number things don't really work well
    minClearings = 4
    minSize = 500
    # A lot of the randomness is based on having 12 clearings. Use this to scale parts of the generation based on the real number
    expectedClearings = 12
    # Clearings won't be spawned outside of this space along the edge of the map
    clearingBufferPercentage = 0.1
    # Size in pixels of the grid cells used in clearing placement
    gridSize = 10
    # Size in pizels of the cells used for drawing
    drawGridCellSize = 4
    drawGridWaterCellsBuffer = 2
    
    pathsTable = [0,0,2,2,3,3,3,4,4,4,5,5,6] #[0,0,1,2,2,3,3,3,3,3,4,4,5] Adding  better weights to the paths here
    residentsTable = ["Rabbit","Mouse","Fox"]
    
    basicNames      = ["Patchwood", "Underleaf", "Pinehorn", "Sundell", "Rooston", "Milltown", "Oakenhold", "Limberly",
                       "Allaburrow", "Flathome", "Tonnery", "Firehollow", "Opensky Haven", "Talon Hill", "Pellenicky Glade",
                       "Hacksaw Dell", "Heartwood", "Sixtoe Stand", "Limmery Post", "Appleloft", "Cutter's Stump", "Greattree"]
    riverNames      = ["Clutcher's Creek", "Sundew Bend", "Alder's Crossing", "Pebblebrook", "Runner's Falls"]
    mountainNames   = ["Ironvein", "Icetrap", "Windgap Refuge", "Gelilah’s Grove", "Goldton", "Climber's Respite",
                       "Snowtown", "Rickert's Mine", "Wolfepoint", "Coolclaw Mine" ]
    lakeNames       = ["Laketown", "Bertram's Cove", "Port Mysk", "Kelian's Bluffs", "Mapleharbor", "Port Sumac",
                       "Stoneshore"]
    riverLakeNames  = ["Blackpaw's Dam", "Riversend", "Grandharbor"]
    marshNames      = ["Wetwood", "Hookfoot Bog", "Milldew", "Orik's Marsh"]

    # It's ok to have duplicates here, we weed them out later
    possibleNames = basicNames + riverNames + mountainNames + lakeNames + riverLakeNames + marshNames

    allNames = {}
    
    cornerNames = ["BL", "BR", "TL", "TR"]
    oppositeCorners = [ 3, 2, 1, 0 ]

    riverfolkValuableResources = []
    nRiverfolkPresences = 4

    numBorderPoints = 2

    # Path draw data
    pathWidth = 4
    pathSegmentLength = 10
    pathSegmentSpacing = 10
    pathPointVariance = 0 # Keep this at 0 because we don't want to have to store all of the path points to do redraws
    
    # What value the roll must be at or above to relinquish control. 13+ is impossible
    marquisateControlVals   = [0,5,7,10,12,13,13,13,13,13,13,13,13]
    eyrieControlVals        = [0,6,9,11,13,13,13,13,13,13,13,13,13]
    eyrieRoostVals          = [0,9,11,12,13,13,13,13,13,13,13,13,13]
    duchyControlVal = 10

    # Decor data
    decorMaxArea = 50000.0
    decorMinArea = 1.0
    decorMaxPointsPerDt = 175
    decorMinPointsPerDt = 1
    mountainChance = 0.4
    marshChance = 0.5
    decorFromClearingBuffer = 25
    maxDecorDistToWater = 10
    maxDecorDistToWaterSq = maxDecorDistToWater * maxDecorDistToWater

    decorMountainPercentage = 0.7
    decorLakePercentage = 0.0
    decorForestPercentage = 1.0
    decorMarshPercentage = 0.9

    treeMaxSize = 30
    treeMinSize = 23

    pineMaxSize = 35
    pineMinSize = 25

    bushMaxSize = 15
    bushMinSize = 7

    mountainMaxSize = 60
    mountainMinSize = 34
    mountainSnowCapMinSize = 42

    marshTreeMaxSize = 30
    marshTreeMinSize = 23

    waveMaxSize = 5
    waveMinSize = 5
    waveWidth = 1

    mountainColourVariance = 10
    treeColourVariance = 25
    marshColourVariance = 25
    pineColourVariance = 15
    bushColourVariance = 30
    
    smallHouseSize = 30

    houseOutlineWidth = 1

    class DecorObjectType(Enum):
        TREE = 0
        MOUNTAIN = 1
        PINE = 2
        BUSH = 3
        
    # Drawing functions
    @staticmethod
    def drawTree( self, screen, pos, size, colour ):
        trunkPoints = [ [-.2, 0], [-.15, -.05], [-.15, -.7], [.15, -.7], [.15, -.05], [.2, 0] ]
        for i in range( len( trunkPoints ) ):
            trunkPoints[i] = pos + size * np.array( trunkPoints[i] )

        pygame.draw.polygon( screen, BROWN, trunkPoints )

        leavesPoints = [ [ pos[0] - 0.25 * size, pos[1] - 0.6 * size ], [ pos[0] + 0.25 * size, pos[1] - 0.6 * size ], [ pos[0], pos[1] - 0.7 * size ] ]
        leavesSizes = [ size * 0.25, size * 0.25, size * 0.35 ]

        for i in range( len( leavesPoints ) ):
            pygame.draw.circle( screen, colour, leavesPoints[i], leavesSizes[i] )
    
    @staticmethod
    def drawMountain( self, screen, pos, size, colour ):
        pos = np.array( pos )
        mountainPoints = ( pos + ( 0, - size ), pos + ( - size / 2, 0 ), pos + ( size / 2, 0 ) )
                        
        pygame.draw.polygon( screen, colour, mountainPoints )
        if size >= self.mountainSnowCapMinSize:
            snowCapHeight = ( size - self.mountainSnowCapMinSize ) / size;
            snowCapPoints = ( mountainPoints[0], mountainPoints[0] + snowCapHeight * ( mountainPoints[1] - mountainPoints[0] ), mountainPoints[0] + snowCapHeight * ( mountainPoints[2] - mountainPoints[0] ) )
            pygame.draw.polygon( screen, WHITE, snowCapPoints )

    @staticmethod
    def drawPine( self, screen, pos, size, colour ):
        trunkPoints = [ [-.15, 0], [-.1, -.1], [.1, -.1], [.15, 0] ]
        for i in range( len( trunkPoints ) ):
            trunkPoints[i] = pos + size * np.array( trunkPoints[i] )

        pygame.draw.polygon( screen, DARK_BROWN, trunkPoints )
        
        treePoints = [ [0, -1.0], [.2, -.7], [.1, -.7], [.3, -.4], [.2, -.4], [.4, -.1], [-.4, -.1], [-.2, -.4], [-.3, -.4], [-.1, -.7], [-.2, -.7] ]
        for i in range( len( treePoints ) ):
            treePoints[i] = pos + size * np.array( treePoints[i] )

        pygame.draw.polygon( screen, colour, treePoints )

    @staticmethod
    def drawBush( self, screen, pos, size, colour ):
        drawPos = [ pos[0], pos[1] - size / 2 ]
        pygame.draw.circle( screen, colour, drawPos, size / 2 )

    @staticmethod
    def drawSmallHouse( self, screen, pos, size, colour ):
        basePoints = [ [-.3, .0], [-.3, -.4], [.0, -.7], [.3, -.4], [.3, .0] ]
        roofPoints = [ [.0, -.7], [.4, -.3], [.45, -.35], [.3, -.5], [.3, -.75], [.15, -.75], [.15, -.65], [0, -.8], [-.45, -.35], [-.4, -.3] ]

        colours = [ GREY, BROWN ]
        allPoints = [ basePoints, roofPoints ]

        for pointsIndex in range( len( allPoints ) ):
            points = allPoints[pointsIndex]
            for i in range( len( points ) ):
                points[i] = pos + size * np.array( points[i] )

            pygame.draw.polygon( screen, colours[pointsIndex], points )
            pygame.draw.polygon( screen, BLACK, points, width=self.houseOutlineWidth )


    # For each DTType, we have the draw Functions and the relative weight to draw them ( Ex 3 trees to every 1 pine )
    dtDrawDataForType = { DTType.FOREST     : ( [ DecorObjectType.TREE, DecorObjectType.PINE, DecorObjectType.BUSH ],
                                                [ 6, 5, 1 ] ),
                          DTType.LAKE       : ( [],
                                                [] ),
                          DTType.MARSH      : ( [ DecorObjectType.TREE, DecorObjectType.BUSH ],
                                                [ 2, 1 ] ),
                          DTType.MOUNTAIN   : ( [ DecorObjectType.MOUNTAIN, DecorObjectType.PINE ],
                                                [ 2, 5 ] ),
    }

    # River data
    riverCloseWeight = 0.65
    riverFarWeight = 0.35
    riverClearingFactor = 0.7
    riverConnectedFactor = 1.3
    riverMaxOffsetDistance = 100

    riverWidthMin = 2
    riverWidthMax = 12
    riverWidthVariance = 4

    # Bridge data
    bridgeHalfWidth = 5
    bridgeHalfSize = 15
    bridgePoleRadius = 2

    # Landmark data
    minLandmarks = 2
    maxLandmarks = 3

    # Lookup tables for what kind of landmark can spawn where
    landmarkLookupTable = { DTType.FOREST   : { LandmarkType.RUIN: True,
                                                LandmarkType.GREATTREE: True,
                                                LandmarkType.CAVE: True,
                                                LandmarkType.BEAR: True,
                                                LandmarkType.ELK: True,
                                                LandmarkType.SHRINE: True,
                                                },
                            DTType.MARSH    : { LandmarkType.RUIN: True,
                                                LandmarkType.GREATTREE: True,
                                                LandmarkType.CAVE: True,
                                                LandmarkType.BEAR: True,
                                                LandmarkType.ELK: True,
                                                },
                            DTType.MOUNTAIN : { LandmarkType.CAVE: True,
                                                LandmarkType.VOLCANO: True,
                                                LandmarkType.SHRINE: True,
                                                },
                            DTType.LAKE     : { LandmarkType.SHIPWRECK: True
                                                },
                            }

    # Update data
    lossControlChance = 0.1

    # Roll fcns
    @staticmethod
    def marquisateRoll( self ):
        numTotal = 0
        
        for clearing in self.clearings:
            if clearing.control == "Marquisate":
                numTotal += 1
            if clearing.hasFeature( "Workshop" ):
                numTotal += 1
            if clearing.hasFeature( "Sawmill" ):
                numTotal += 1
            if clearing.hasFeature( "Recruiter" ):
                numTotal += 1

        # Originally 4, scaled down
        numFeaturesForBonus = self.scaleByExpectedClearings( 2 )
        if numTotal > numFeaturesForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def eyrieRoll( self ):
        numRoosts = 0
        numClearings = 0
        
        for clearing in self.clearings:
            if clearing.control == "Eyrie":
                numClearings += 1
                
            if clearing.hasFeature( "Roost" ):
                numRoosts += 1

        # Originally 1
        numRoostsForBonus = self.scaleByExpectedClearings( 0 )
        # Originally 3
        numClearingsForBonus = self.scaleByExpectedClearings( 2 )
        if numRoosts > numRoostsForBonus or numClearings > numClearingsForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def allianceRoll( self ):
        numBases = 0
        numSympathy = 0
        
        for clearing in self.clearings:
            if clearing.hasFeature( "Base" ):
                numBases += 1
            if clearing.hasFeature( "Woodland Alliance Support" ):
                numSympathy += 1

        # Originally 0
        numBasesForBonus = self.scaleByExpectedClearings( 1 )
        # Originally 2
        numSympathyForBonus = self.scaleByExpectedClearings( 3 )
        if numBases > numBasesForBonus or numSympathy > numSympathyForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def lizardCultRoll( self ):
        numGardens = 0
        
        for clearing in self.clearings:
            if clearing.hasFeature( "Garden" ):
                numGardens += 1

        # Originally 1
        numGardensForBonus = self.scaleByExpectedClearings( 1 )
        if numGardens > numGardensForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def riverfolkRoll( self ):
        numPosts = 0
        
        for clearing in self.clearings:
            if clearing.hasFeature( "Riverfolk" ):
                numPosts += 1

        # Originally 2
        numPostsForBonus = self.scaleByExpectedClearings( 3 )
        if numPosts > numPostsForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def duchyRoll( self ):
        numClearings = 0
        numMarkets = 0
        numCitadels = 0
        
        for clearing in self.clearings:
            if clearing.control == "Grand Duchy":
                numClearings += 1
                
            if clearing.hasFeature( "Market" ):
                numMarkets += 1
            if clearing.hasFeature( "Citadel" ):
                numCitadels += 1
                
        # Originally 1
        numClearingsForBonus = self.scaleByExpectedClearings( 1 )
        # Originally 0
        numMarketsForBonus = self.scaleByExpectedClearings( 0 )
        # Originally 0
        numCitadelsForBonus = self.scaleByExpectedClearings( 0 )
        if numClearings > numClearingsForBonus and numMarkets > numMarketsForBonus and numCitadels > numCitadelsForBonus:
            return 1
        else:
            return 0

    @staticmethod
    def corvidRoll( self ):
        numPlots = 0
        
        for clearing in self.clearings:
            if clearing.control == "Corvid Conspiracy":
                numPlots += 1

        # Originally 2
        numPlotsForBonus = self.scaleByExpectedClearings( 3 )
        if numPlots > numPlotsForBonus:
            return 1
        else:
            return 0

    possibleBuildingLosses = { "Marquisate": ["Stronghold", "Sawmill", "Recruiter", "Workshop"],
                    "Eyrie": ["Roost"],
                    "Woodland Alliance": ["Base", "Woodland Alliance Support"],
                    "Lizard Cult": ["Garden", "Lizard Cult Support", "In Progress Garden"],
                    "Riverfolk": ["Riverfolk", "Trading Post"],
                    "Grand Duchy": ["Tunnel", "Market", "Citadel"],
                    "Corvid Conspiracy": ["Corvid Conspiracy", "Plot"],
                    }

    # Minor boon fcns
    @staticmethod
    def attack( self, faction ):
        adjacent = [False for i in range(len(self.clearings))]
        numControlled = 0
        
        for clearing in self.clearings:
            if clearing.control == faction:
                numControlled += 1
                for other in clearing.connected:
                    if other.control != faction:
                        adjacent[other.id] = True
                if clearing.hasFeature( "Lake" ) or clearing.hasFeature( "River" ):
                    for other in self.clearings:
                        if clearing.id != clearing.id and ( other.hasFeature( "Lake" ) or other.hasFeature( "River" ) ):
                            adjacent[other.id] = True
                            
            elif faction == "Grand Duchy" and clearing.hasFeature( "Tunnel" ):
                adjacent[clearing.id] = True

        canAttack = []
        for i in range( len( adjacent) ):
            if adjacent[i]:
                canAttack.append( self.clearings[i] )

        if numControlled == 0:
            canAttack += self.corners

        if len( canAttack ) == 0:
            return

        numToAttack = self.scaleByExpectedClearings( 1 )
        numToAttack = int( min( numToAttack, len( canAttack ) ) )
        toAttackClearings = random.sample( canAttack, numToAttack )

        for toAttack in toAttackClearings:
            toAttack.increaseWarStatusBy( 1 )
            
            if toAttack.hasFeature( "Fortifications" ):
                toAttack.removeFeature( "Fortifications" )
                return
            
            blockingFeatures = [ "Roost", "Base", "Stronghold", "Workshop", "Sawmill", "Recruiter", "Citadel", "Market" ]
            hasBlocking = False
            for blocking in blockingFeatures:
                if toAttack.hasFeature( blocking ):
                    toAttack.removeFeature( blocking )
                    hasBlocking = True

            if not hasBlocking:
                # Clear out the previous plots and trade posts that aren't blocking features
                if toAttack.control in self.possibleBuildingLosses:
                    for building in self.possibleBuildingLosses[ toAttack.control ]:
                        toAttack.removeFeature( building )
                toAttack.control = faction
                if faction == "Marquisate" and numControlled == 0:
                    toAttack.addFeature( "Stronghold" )

                if faction == "Eyrie" and numControlled == 0:
                    toAttack.addFeature( "Roost" )

    @staticmethod
    def fortify( self, faction ):
        controlled = []

        strongholdExists = False
        for clearing in self.clearings:
            if clearing.control == faction and not clearing.hasFeature( "Fortifications" ):
                controlled.append( clearing )
            if clearing.hasFeature( "Stronghold" ):
                strongholdExists = True

        if len( controlled ) == 0:
            return
        
        numToFortify = self.scaleByExpectedClearings( 1, 1 )
        numToFortify = min( len( controlled ), numToFortify )
        toFortifyClearings = random.sample( controlled, numToFortify )

        for toFortify in toFortifyClearings:
            toFortify.addFeature( "Fortifications" )

            if faction == "Marquisate" and not strongholdExists:
                toFortify.addFeature( "Stronghold" )

    @staticmethod
    def establishCells( self, faction ):
        notControlled = []

        for clearing in self.clearings:
            if clearing.control != faction and not clearing.hasFeature( "Woodland Alliance Support" ):
                notControlled.append( clearing )

        # Originally 2
        numClearingsToSpreadTo = self.scaleByExpectedClearings( 2, 1 )
        numAlliance = int( min( numClearingsToSpreadTo, len( notControlled ) ) )

        if numAlliance > 0:
            toAlliance = random.sample( notControlled, numAlliance )

            for clearing in toAlliance:
                clearing.addFeature( "Woodland Alliance Support" )

    @staticmethod
    def stampCells( self, faction ):
        for clearing in self.clearings:
            if clearing.control == faction:
                clearing.removeFeature( "Woodland Alliance Support" )

    @staticmethod
    def buildIndustry( self, faction ):
        controlled = []

        for clearing in self.clearings:
            if clearing.control == faction and not( clearing.hasFeature( "Sawmill" ) and clearing.hasFeature( "Workshop" ) and clearing.hasFeature( "Recruiter" ) ):
                controlled.append( clearing )
        
        if len( controlled ) > 0:
            random.shuffle( controlled )

            # Originally 1
            numToBuild = self.scaleByExpectedClearings( 1, 1 )
            numToBuild = min( len( controlled ), numToBuild )
            toAdd = random.sample( controlled, numToBuild )

            for clearing in toAdd:
                if not clearing.hasFeature( "Sawmill" ):
                    clearing.addFeature( "Sawmill" )
                elif not clearing.hasFeature( "Workshop" ):
                    clearing.addFeature( "Workshop" )
                elif not clearing.hasFeature( "Recruiter" ):
                    clearing.addFeature( "Recruiter" )

    @staticmethod
    def buildGarden( self, faction ):
        almostBuilt = []
        canBuild = []

        for clearing in self.clearings:
            if clearing.hasFeature( "In Progress Garden" ):
                almostBuilt.append( clearing )

            if not clearing.hasFeature( "In Progress Garden" ) and not clearing.hasFeature( "Garden" ) and ( clearing.hasFeature( "Lizard Cult Support" ) or clearing.control == faction ):
                canBuild.append( clearing )

        if len( almostBuilt ) > 0:
            # Originally 1
            numToBuild = self.scaleByExpectedClearings( 1, 1 )
            numToBuild = min( numToBuild, len( almostBuilt ) )
            toBuild = random.sample( almostBuilt, numToBuild )
    
            for clearing in toBuild:
                clearing.addFeature( "Garden" )
                clearing.removeFeature( "In Progress Garden" )
                
        elif len( canBuild ) > 0:
            # Originally 1
            numToBuild = self.scaleByExpectedClearings( 1, 1 )
            numToBuild = min( numToBuild, len( canBuild ) )
            toBuild = random.sample( canBuild, numToBuild )

            for clearing in toBuild:
                clearing.addFeature( "In Progress Garden" )
                
    @staticmethod
    def proselytize( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if not clearing.control == faction and not clearing.hasFeature( "Lizard Cult Support" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            # Originally 1
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAdd = random.sample( canAdd, numToAdd )

            for clearing in toAdd:
                clearing.addFeature( "Lizard Cult" )
            
    @staticmethod
    def conductCommerce( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if not clearing.control == faction and not clearing.hasFeature( "Riverfolk" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            # Originally 1
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAdd = random.sample( canAdd, numToAdd )

            for clearing in toAdd:
                clearing.addFeature( "Riverfolk" )
            
    @staticmethod
    def buildTradingPost( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if clearing.hasFeature( "Riverfolk" ) and not clearing.hasFeature( "Trading Post" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            # Originally 1
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAdd = random.sample( canAdd, numToAdd )

            for clearing in toAdd:
                clearing.addFeature( "Trading Post" )

    @staticmethod
    def connectTunnel( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if not clearing.hasFeature( "Tunnel" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            # Originally 1
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAdd = random.sample( canAdd, numToAdd )

            for clearing in toAdd:
                clearing.addFeature( "Tunnel" )

    @staticmethod
    def buildDuchy( self, faction ):
        controlled = []

        for clearing in self.clearings:
            if clearing.control == faction and not( clearing.hasFeature( "Market" ) and clearing.hasFeature( "Citadel" ) ):
                controlled.append( clearing )
        
        if len( controlled ) > 0:
            # Originally 1
            numToBuild = self.scaleByExpectedClearings( 1, 1 )
            numToBuild = min( numToBuild, len( controlled ) )
            toBuild = random.sample( controlled, numToBuild )

            for clearing in toBuild:
                if not clearing.hasFeature( "Market" ):
                    clearing.addFeature( "Market" )
                elif not clearing.hasFeature( "Citadel" ):
                    clearing.addFeature( "Citadel" )
        
    @staticmethod
    def expandNetwork( self, faction ):
        adjacent = [False for i in range(len(self.clearings))]

        for clearing in self.clearings:
            if clearing.control == faction:
                for other in clearing.connected:
                    if other.control != faction:
                        adjacent[other.id] = True

                if clearing.hasFeature( "Lake" ) or clearing.hasFeature( "River" ):
                    for other in self.clearings:
                        if clearing.id != clearing.id and ( other.hasFeature( "Lake" ) or other.hasFeature( "River" ) ):
                            adjacent[other.id] = True

        canAdd = []
        for i in range( len( adjacent) ):
            if adjacent[i] and not self.clearings[i].hasFeature( "Corvid Conspiracy" ):
                canAdd.append( self.clearings[i] )

        if len( canAdd ) == 0:
            return

        numToAdd = self.scaleByExpectedClearings( 1, 1 )
        numToAdd = min( numToAdd, len( canAdd ) )
        toAddClearings = random.sample( canAdd, numToAdd )

        for toAdd in toAddClearings:
            toAdd.addFeature( "Corvid Conspiracy" )
        
    @staticmethod
    def enactPlot( self, faction ):
        controlled = []
        for clearing in self.clearings:
            if clearing.hasFeature( "Corvid Conspiracy" ) and not clearing.hasFeature( "Plot" ):
                controlled.append( clearing )

        if len( controlled ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( controlled ) )
            toAddClearings = random.sample( controlled, numToAdd )

            for toAdd in toAddClearings:
                toAdd.addFeature( "Plot" )
                
    @staticmethod
    def stampPlot( self, faction ):
        for clearing in self.clearings:
            if clearing.control == faction:
                clearing.removeFeature( "Plot" )
                clearing.removeFeature( "Corvid Conspiracy" )

    @staticmethod
    def evictTraders( self, faction ):
        for clearing in self.clearings:
            if clearing.control == faction:
                if clearing.hasFeature( "Trading Post" ):
                    clearing.removeFeature( "Trading Post" )
                else:
                    clearing.removeFeature( "Riverfolk" )

    @staticmethod
    def lossUpdate( self, faction ):
        control = []
        buildings = []
        for clearing in self.clearings:
            if clearing.control == faction:
                control.append( clearing )

                if clearing.hasFeature( "Fortifications" ):
                    buildings.append([clearing, "Fortifications"])

            for building in self.possibleBuildingLosses[ faction ]:
                if clearing.hasFeature( building ):
                    buildings.append([clearing, building])
                
        chance = random.random()

        # Either lose control or lose a building
        if chance < self.lossControlChance and len( control ) > 0:
            numToLose= self.scaleByExpectedClearings( 1, 1 )
            numToLose = min( numToLose, len( control ) )
            toLoseClearings = random.sample( control, numToLose )

            for toLose in toLoseClearings:
                toLose.control = "None"
                toLose.removeFeature( "Fortifications" )

                for building in self.possibleBuildingLosses[ faction ]:
                    toLose.removeFeature( building )
        elif len( buildings ) > 0:
            numToLose = self.scaleByExpectedClearings( 1, 1 )
            numToLose = min( numToLose, len( buildings ) )
            toLoseData = random.sample( buildings, numToLose )
            
            for toLose in toLoseData:
                toLose[0].removeFeature( toLose[1] )

    # Major boons
    @staticmethod
    def revolt( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if clearing.hasFeature( "Woodland Alliance Support" ) and not clearing.hasFeature( "Base" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAddClearings = random.sample( canAdd, numToAdd )

            for toAdd in toAddClearings:
                toAdd.addFeature( "Base" )

                toAdd.removeFeature( "Fortifications" )

                if toAdd.control in self.possibleBuildingLosses:
                    for building in self.possibleBuildingLosses[ toAdd.control ]:
                        toAdd.removeFeature( building )

                toAdd.increaseWarStatusBy( 1 )
                toAdd.control = "Woodland Alliance"

    @staticmethod
    def buildRoost( self, faction ):
        canAdd = []
        for clearing in self.clearings:
            if clearing.control == faction and not clearing.hasFeature( "Roost" ):
                canAdd.append( clearing )

        if len( canAdd ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAddClearings = random.sample( canAdd, numToAdd )

            for toAdd in toAddClearings:
                toAdd.addFeature( "Roost" )

    @staticmethod
    def rapidBuildGarden( self, faction ):
        controlled = []

        for clearing in self.clearings:
            if not clearing.hasFeature( "Garden" ) and not clearing.hasFeature( "Garden In Progress" ) and clearing.hasFeature( "Lizard Cult Support" ):
                controlled.append( clearing )
        
        if len( controlled ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( controlled ) )
            toAddClearings = random.sample( controlled, numToAdd )

            for toAdd in toAddClearings:
                toAdd.addFeature( "Garden" )
                toAdd.control = "Lizard Cult"

    @staticmethod
    def tradeWar( self, faction ):
        canAdd = []

        for clearing in self.clearings:
            if clearing.hasFeature( "Trading Post" ):
                canAdd.append( clearing )
        
        if len( canAdd ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAddClearings = random.sample( canAdd, numToAdd )

            for toAdd in toAddClearings:
                toAdd.removeFeature( "Fortifications" )

                if toAdd.control in self.possibleBuildingLosses:
                    for building in self.possibleBuildingLosses[ toAdd.control ]:
                        toAdd.removeFeature( building )

                toAdd.increaseWarStatusBy( 1 )
                toAdd.control = "Riverfolk"

                for adjacent in toAdd.connected:
                    if not adjacent.hasFeature( "Trading Post" ):
                        adjacent.addFeature( "Trading Post" )
                        break

    @staticmethod
    def culminatePlot( self, faction ):
        canAdd = []

        for clearing in self.clearings:
            if clearing.hasFeature( "Plot" ) and clearing.control != faction:
                canAdd.append( clearing )
        
        if len( canAdd ) > 0:
            numToAdd = self.scaleByExpectedClearings( 1, 1 )
            numToAdd = min( numToAdd, len( canAdd ) )
            toAddClearings = random.sample( canAdd, numToAdd )

            for toAdd in toAddClearings:
                toAdd.removeFeature( "Fortifications" )

                if toAdd.control in self.possibleBuildingLosses:
                    for building in self.possibleBuildingLosses[ toAdd.control ]:
                        toAdd.removeFeature( building )

                toAdd.increaseWarStatusBy( 1 )
                toAdd.control = "Corvid Conspiracy"
                
    # minor, major, loss
    controlFcns = { "Marquisate":           [marquisateRoll,    [attack, fortify, stampCells, buildIndustry, stampPlot, evictTraders],              [],                 [lossUpdate, None]],
                    "Eyrie":                [eyrieRoll,         [attack, fortify, stampCells, stampPlot, evictTraders],                             [buildRoost],       [lossUpdate, None]],
                    "Woodland Alliance":    [allianceRoll,      [attack, fortify, establishCells, stampPlot, evictTraders],                         [revolt],           [lossUpdate, None]],
                    "Lizard Cult":          [lizardCultRoll,    [attack, fortify, stampCells, buildGarden, proselytize, stampPlot, evictTraders],   [rapidBuildGarden], [lossUpdate, None]],
                    "Riverfolk":            [riverfolkRoll,     [fortify, stampCells, conductCommerce, buildTradingPost, stampPlot],                [tradeWar],         [lossUpdate, None]],
                    "Grand Duchy":          [duchyRoll,         [attack, fortify, connectTunnel, buildDuchy, stampCells, stampPlot, evictTraders],  [],                 [lossUpdate, None]],
                    "Corvid Conspiracy":    [corvidRoll,        [attack, fortify, stampCells, expandNetwork, enactPlot, evictTraders],              [culminatePlot],    [lossUpdate, None]],
                    }

    # Initialization
    def __init__( self, pos, size, minClearingDist, enableLake=True, enableRiver=True, forceLake=False, forceRiver=False, enableMarquisate=True, enableEyrie=True, enableWoodlandAlliance=True,
                  enableLizardCult=True, enableRiverfolk=True, enableDuchy=True, enableCorvids=True, enableMountains=True, enableMarshes=True, enableLandmarks=True ):
        self.pos = pos
        self.size = [ max( size[0], self.minSize ), max( size[1], self.minSize ) ]
        self.minClearingDist = max( 10, minClearingDist )
        
        self.rect = [ self.pos[0], self.pos[1], self.size[0], self.size[1] ]
        self.bottom     = self.pos[1]
        self.left       = self.pos[0]
        self.top        = self.pos[1] + self.size[1]
        self.right      = self.pos[0] + self.size[0]
        self.area       = self.size[1] * self.size[0]
        self.woodlandBottom     = self.bottom + int( self.clearingBufferPercentage * self.size[1] )
        self.woodlandLeft       = self.left + int( self.clearingBufferPercentage * self.size[0] )
        self.woodlandTop        = self.top - int( self.clearingBufferPercentage * self.size[1] )
        self.woodlandRight      = self.right - int( self.clearingBufferPercentage * self.size[0] )
        self.minClearingDistSq = self.minClearingDist * self.minClearingDist
        
        self.tri = None
        self.dtTypes = []
        self.decorPointsForDts = []
        self.decorSizesForDts = []
        self.decorColoursForDts = []
        
        self.clearings = []
        self.paths = []
        self.corners = []
        self.water = None
        self.lakeClearings = []
        self.lakeTris = []
        self.riverSplinePoints = []
        self.riverControlPoints = []
        self.riverHullPoints = []
        self.bridges = []
        self.allNames = {}
        
        self.drawGridSize = [ int( self.size[0] / self.drawGridCellSize ) + 1, int( self.size[1] / self.drawGridCellSize ) + 1 ]
        self.drawGridOpenCells = [ [ True for _ in range( self.drawGridSize[1] ) ] for _ in range( self.drawGridSize[0] ) ]
        self.drawGridData = [ [] for _ in range( self.drawGridSize[1] ) ]

        self.controlCountingData = { "Marquisate": [[], [], []],
                    "Eyrie": [[], [], []],
                    "Woodland Alliance": [[], [], []],
                    "Lizard Cult": [[], [], []],
                    "Riverfolk": [[], [], []],
                    "Grand Duchy": [[], [], []],
                    "Corvid Conspiracy": [[], [], []],
                    "None": [[], [], []],
                    }

        self.forceLake = forceLake
        self.forceRiver = forceRiver
        
        self.enableLake = enableLake
        self.enableRiver = enableRiver
        
        self.enableMarquisate = enableMarquisate
        self.enableEyrie = enableEyrie
        self.enableWoodlandAlliance = enableWoodlandAlliance
        self.enableLizardCult = enableLizardCult
        self.enableRiverfolk = enableRiverfolk
        self.enableDuchy = enableDuchy
        self.enableCorvids = enableCorvids

        self.enabledFactions = { "Marquisate"           : self.enableMarquisate,
                                 "Eyrie"                : self.enableEyrie,
                                 "Woodland Alliance"    : self.enableWoodlandAlliance,
                                 "Lizard Cult"          : self.enableLizardCult,
                                 "Riverfolk"            : self.enableRiverfolk,
                                 "Grand Duchy"          : self.enableDuchy,
                                 "Corvid Conspiracy"    : self.enableCorvids,
                                 }

        self.enableMountains = enableMountains
        self.enableMarshes = enableMarshes
        self.enableLandmarks = enableLandmarks

        
    def update( self ):
        factionControl = [ [ 0, list( self.controlFcns.keys() )[i] ] for i in range( len( self.controlFcns ) ) ]

        for control in self.controlCountingData:
            self.controlCountingData[control][0].append(0)
            self.controlCountingData[control][1].append(0)
            self.controlCountingData[control][2].append(0)
            
        for clearing in self.clearings:
            for i in range( len( factionControl ) ):
                if clearing.control == factionControl[i][1]:
                    factionControl[i][0] += 1

        factionControl.sort(key=lambda x:x[0], reverse=True)
        
        for factionIndex in range( len( factionControl ) ):
            factionName = factionControl[factionIndex][1]

            if self.enabledFactions[ factionName ]:
                numControl = factionControl[factionIndex][0]
                rollFcn = self.controlFcns[ factionName ][0]
                minorBoonFcns = self.controlFcns[ factionName ][1]
                majorBoonFcns = self.controlFcns[ factionName ][2]
                lossFcns = self.controlFcns[ factionName ][3]

                rollBonus = rollFcn( self )
                
                roll = rollDie( 6, 2 ) + rollBonus
                if factionIndex == 0:
                    roll -= 1
                if numControl == 0:
                    roll += 2

                # Counting the roll data to see how good the values guys get
                self.controlCountingData[ factionName ][2].append( roll )
                
                toCall = []
                
                if roll >= 10:
                    # If we don't have any major boons do two minor boons
                    if ( len( majorBoonFcns ) == 0 or random.random() < 0.5 ) and len( minorBoonFcns ) > 0:
                        toCall = np.random.choice( minorBoonFcns, 2, replace=True )
                    elif len( majorBoonFcns ) > 0:
                        toCall = random.sample( majorBoonFcns, 1 )
                elif roll >= 7 and len( minorBoonFcns ) > 0:
                    toCall = random.sample( minorBoonFcns, 1 )
                elif len( lossFcns ) > 0:
                    toCall = random.sample( lossFcns, 1 )

                for call in toCall:
                    if call != None:
                        call( self, factionName )

        # This is debug data for counting how much control each faction has        
        for clearing in self.clearings:
            control = clearing.control
            if control in self.controlCountingData:
                self.controlCountingData[ control ][0][-1] += 1

            for feature in clearing.features:
                fcontrol = Clearing.featuresDict[ feature ][0]
                if fcontrol != None and fcontrol in self.controlCountingData:
                    self.controlCountingData[ fcontrol ][1][-1] += 1

        for clearing in self.clearings:
            clearing.update()


    def printControlDebug( self ):
        nc = 0
        for control in self.controlCountingData:
            print( control + " " + str( np.average( self.controlCountingData[control][0] ) ) )
            nc = len( self.controlCountingData[control][0] )
        print(" ")
        for control in self.controlCountingData:
            print( control + " building " + str( np.average( self.controlCountingData[control][1] ) ) )
        print(" ")
        for control in self.controlCountingData:
            print( control + " ave roll " + str( np.average( self.controlCountingData[control][2] ) ) )
        print( " ---------- " + str(nc))

    def scaleByExpectedClearings( self, num, minVal=0 ):
        val = num * len( self.clearings ) / self.expectedClearings
        return int( max( minVal, val ) )

    def clearData( self ):
        self.tri = None
        self.dtTypes = []
        self.decorPointsForDts = []
        self.decorSizesForDts = []
        self.decorColoursForDts = []
        
        self.clearings = []
        self.paths = []
        self.corners = []
        self.water = None
        self.lakeClearings = []
        self.lakeTris = []
        self.riverSplinePoints = []
        self.riverControlPoints = []
        self.riverHullPoints = []
        self.bridges = []
        self.allNames = {}
        
    def generate( self, numClearings ):
        numClearings = max( self.minClearings, numClearings )
        
        self.clearData()
        
        self.generateNameData()
        
        self.generateClearings( numClearings )
        
        self.generateTriData()
        
        self.generatePaths()
        
        self.generateWater()
        
        self.calcCorners()
        self.generateWoodlandControl()

        self.generateDrawGrid()
        self.generateDecorData()
        self.generateClearingDecor()

        self.generateLandmarks()
        
        # Do this near the end since we want to check what places are next to rivers, lakes, etc.
        self.generateClearingNames()
        self.generateClearingLocalData()

    def draw( self, screen ):
        # Draw everything here in reverse order of what we want on top
        pygame.draw.rect( screen, LIGHT_GREEN, self.rect )

        if self.water:
            self.water.draw( screen )

        self.drawBridges( screen )
        self.drawDecor( screen )
        self.drawPaths( screen )
        self.drawLandmarks( screen )
            
        pygame.draw.rect( screen, BROWN, self.rect, width=5 )
        
        for clearing in self.clearings:
            clearing.draw( screen )
        
        
    def drawPaths( self, screen ):
        for path in self.paths:
            startPoint = path.clearing1.pos
            endPoint = path.clearing2.pos

            v = endPoint - startPoint
            l = np.linalg.norm( endPoint - startPoint )
            u = v / l
            d = 0

            while ( d < l ):
                p1 = startPoint + d * u
                p2 = startPoint + min( l, d + self.pathSegmentLength ) * u

                # Variance to make the lines look nicer
                p1 += ( random.uniform( -self.pathPointVariance, self.pathPointVariance ), random.uniform( -self.pathPointVariance, self.pathPointVariance ) )
                p2 += ( random.uniform( -self.pathPointVariance, self.pathPointVariance ), random.uniform( -self.pathPointVariance, self.pathPointVariance ) )
                pygame.draw.line( screen, RED, p1, p2, self.pathWidth )

                d += self.pathSegmentSpacing + self.pathSegmentLength
        
    def drawDecor( self, screen ):
        # Draw the decor starting from the lowest y to the highest so it's draw on top of themselves
        for j in range( self.drawGridSize[1] ):
            for data in self.drawGridData[j]:
                x = data[0]
                size = data[1]
                colour = data[2]
                drawFcn = data[3]

                pos = [ x, self.pos[1] + self.drawGridCellSize * j ]

                drawFcn( self, screen, pos, size, colour )

    def drawBridges( self, screen ):
        for bridge in self.bridges:
            pygame.draw.polygon( screen, BROWN, bridge )

            for point in bridge:
                pygame.draw.circle( screen, BROWN, point, self.bridgePoleRadius )
                pygame.draw.circle( screen, BLACK, point, self.bridgePoleRadius, 1 )

    def drawLandmarks( self, screen ):
        for landmark in self.landmarks:
            landmark.draw( screen )

    def generateNameData( self ):
        for name in self.possibleNames:
            if not name in self.allNames:
                self.allNames[name] = False

        allNames = {}
        
    def generatePointsInTri( self, a, b, c, n ):
        # These vectors define the plane the points can be in, with randomly choosing a as the origin
        ba = b - a
        ca = c - a

        points = []
        for i in range(n):
            u1 = random.random()
            u2 = random.random()

            # u1 and u2 will give us a random point inside the quadrilateral made by ba and ca, but we want inside the triangle
            # So if any points are past this line (u1+u2 = 1) then flip them so they're inside the original triangle
            if u1 + u2 > 1:
                u1 = 1 - u1
                u2 = 1 - u2

            p = a + u1*ba + u2*ca

            i, j = self.getDrawGridIndexes( p[0], p[1] )
            
            # if we aren't drawing on top of a bad place
            if self.drawGridOpenCells[i][j]:
                points.append(p)

        return points


    def getDrawGridIndexes( self, x, y ):
        i = int( min( self.drawGridSize[0] - 1, max( 0, ( x - self.pos[0] ) / self.drawGridCellSize ) ) )
        j = int( min( self.drawGridSize[1] - 1, max( 0, ( y - self.pos[1] ) / self.drawGridCellSize ) ) )
        return i, j

    def floodFillDrawGrid( self, i, j ):
        toFill = [ [i, j] ]

        while len( toFill ) > 0:
            point = toFill[-1]
            toFill.pop()
            
            if point[0] < 0 or point[0] >= self.drawGridSize[0] or point[1] < 0 or point[1] >= self.drawGridSize[1]:
                continue
            if not self.drawGridOpenCells[point[0]][point[1]]:
                continue
            
            self.drawGridOpenCells[point[0]][point[1]] = False
            toFill.append( [ point[0] - 1, point[1] ] )
            toFill.append( [ point[0] + 1, point[1] ] )
            toFill.append( [ point[0], point[1] - 1 ] )
            toFill.append( [ point[0], point[1] + 1 ] )
            

    def generateDrawGrid( self ):
        self.drawGridOpenCells = [ [ True for _ in range( self.drawGridSize[1] ) ] for _ in range( self.drawGridSize[0] ) ]

        fillPoints = []
        fillPoints.extend( self.riverSplinePoints )
        if self.water:
            fillPoints.extend( self.water.hull )
            
        # Prevent us from drawing on top of water
        for point in fillPoints:
            i, j = self.getDrawGridIndexes( point[0], point[1] )

            minX = int( max( 0, i - self.drawGridWaterCellsBuffer ) )
            maxX = int( min( self.drawGridSize[0], i + self.drawGridWaterCellsBuffer + 1 ) )
            minY = int( max( 0, j - self.drawGridWaterCellsBuffer ) )
            maxY = int( min( self.drawGridSize[1], j + self.drawGridWaterCellsBuffer + 1 ) )

            bufferDistSq = self.drawGridWaterCellsBuffer * self.drawGridWaterCellsBuffer

            for x in range( minX, maxX ):
                for y in range( minY, maxY ):
                    if distSq( np.array([i, j]), np.array([x, y]) ) <= bufferDistSq:
                        self.drawGridOpenCells[x][y] = False

        # Fill in the lake if it exists
        for triIndex in self.water.triangles:
            centroid = np.array([0.0, 0.0])
            dt = self.tri.simplices[triIndex]
            for pointIndex in dt:
                centroid += self.tri.points[pointIndex]

            centroid /= 3
            
            i, j = self.getDrawGridIndexes( centroid[0], centroid[1] )
            # If this point is already filled in, it's probably on the edge and we don't want to fill it in
            if self.drawGridOpenCells[i][j]:
                self.floodFillDrawGrid( i, j )


    def debugDrawDrawGrid( self, screen ):
        for i in range( self.drawGridSize[0] ):
            for j in range( self.drawGridSize[1] ):
                if not self.drawGridOpenCells[i][j]:
                    pygame.draw.rect( screen, RED, [ self.pos[0] + i * self.drawGridCellSize, self.pos[1] + j * self.drawGridCellSize, self.drawGridCellSize, self.drawGridCellSize ] )
                            
        
    def generateDecorData( self ):
        numClearings = len(self.clearings)
        numTris = len( self.tri.simplices )

        self.decorPointsForDts = [ [] for i in range( numTris ) ]
        self.decorSizesForDts = [ [] for i in range( numTris ) ]
        self.decorColoursForDts = [ [] for i in range( numTris ) ]

        areaToPointsFactor = ( self.decorMaxPointsPerDt - self.decorMinPointsPerDt ) / ( self.decorMaxArea - self.decorMinArea )
        
        for dt in range( numTris ):
            a = self.tri.points[ self.tri.simplices[dt][0] ]
            b = self.tri.points[ self.tri.simplices[dt][1] ]
            c = self.tri.points[ self.tri.simplices[dt][2] ]
            points = [a, b, c]
            pointIndexes = [self.tri.simplices[dt][0], self.tri.simplices[dt][1], self.tri.simplices[dt][2]]
            oppPointIndexes = [ [ pointIndexes[1], pointIndexes[2] ], [ pointIndexes[0], pointIndexes[2] ], [ pointIndexes[0], pointIndexes[1] ] ]
            
            area = 0.5 * ( a[0] * ( b[1] - c[1] ) + b[0] * ( c[1] - a[1] ) + c[0] * ( a[1] - b[1] ) )
            # Scale the area to between the bounds so we don't get weird numbers of points
            area = min( self.decorMaxArea, area )
            area = max( self.decorMinArea, area )
            
            numDecorPoints = int( ( area - self.decorMinArea ) * areaToPointsFactor + self.decorMinPointsPerDt )

            # If any of these points is a clearing, then we dont want to draw stuff along the paths or too close to the clearing so offset it
            for i in range( len( points ) ):
                pointOffset = np.array((0.0, 0.0))
                if pointIndexes[i] < numClearings:
                    clearing = self.clearings[ pointIndexes[i] ]
                    oppIndex1 = oppPointIndexes[i][0]
                    oppIndex2 = oppPointIndexes[i][1]
                    
                    if oppIndex1 < numClearings and clearing.isConnectedTo( oppIndex1 ):
                        toOpp = self.tri.points[oppIndex2] - points[i]
                        toOppLen = np.linalg.norm( toOpp )
                        toOpp = toOpp / toOppLen
                        pointOffset += toOpp

                    if oppIndex2 < numClearings and clearing.isConnectedTo( oppIndex2 ):
                        toOpp = self.tri.points[oppIndex1] - points[i]
                        toOppLen = np.linalg.norm( toOpp )
                        toOpp = toOpp / toOppLen
                        pointOffset += toOpp
                        
                pointOffsetLen = np.linalg.norm( pointOffset )
                if pointOffsetLen > 0:
                    pointOffest = pointOffset / pointOffsetLen

                points[i] = points[i] + pointOffset * self.decorFromClearingBuffer
    
            self.decorPointsForDts[dt] = self.generatePointsInTri( points[0], points[1], points[2], numDecorPoints )
            
            # If any of these tri areas is an edge point, then randomly chance it turning into a mountain region
            isEdge = -1 in self.tri.neighbors[dt]
            if ( self.enableMountains and isEdge and self.dtTypes[dt] != DTType.LAKE ):
                mountainChance = random.random()
                if mountainChance < self.mountainChance:
                    self.dtTypes[dt] = DTType.MOUNTAIN

                    # Mark any clearing connected to this tri as a mountainous clearing
                    for vertex in self.tri.simplices[dt]:
                        if vertex < numClearings:
                            if not self.clearings[vertex].hasFeature( "Mountain" ):
                                self.clearings[vertex].addFeature( "Mountain" )

            # If we're a forest next to a lake or have a river clearing adjacent then have a chance to be a marsh
            if ( self.enableMarshes and self.dtTypes[dt] == DTType.FOREST ):
                # Are we next to a lake
                nextToLake = False
                for neighbor in self.tri.neighbors[dt]:
                    if self.dtTypes[neighbor] == DTType.LAKE:
                        nextToLake = True

                # Are we on a river
                # Use tris that have two points connected to rivers. This will make the marshes cross rivers more often and look better
                numAdjacentRiverClearings = 0
                for vertex in self.tri.simplices[dt]:
                    if vertex < numClearings:
                        if self.clearings[vertex].hasFeature( "River" ):
                            numAdjacentRiverClearings += 1

                canBeMarsh = nextToLake or numAdjacentRiverClearings > 1

                # Random chance to become a marsh
                if canBeMarsh:
                    marshChance = random.random()
                    if ( marshChance < self.marshChance ):
                        self.dtTypes[dt] = DTType.MARSH

                        # Mark any clearing connected to this tri as a marsh clearing
                        for vertex in self.tri.simplices[dt]:
                            if vertex < numClearings:
                                if not self.clearings[vertex].hasFeature( "Marsh" ):
                                    self.clearings[vertex].addFeature( "Marsh" )
            

            numPoints = len( self.decorPointsForDts[dt] )

            if self.dtTypes[dt] == DTType.MOUNTAIN:
                numPoints = min( numPoints, int( numPoints * self.decorMountainPercentage ) )
            elif self.dtTypes[dt] == DTType.FOREST:
                numPoints = min( numPoints, int( numPoints * self.decorForestPercentage ) )
            elif self.dtTypes[dt] == DTType.LAKE:
                numPoints = 0
            elif self.dtTypes[dt] == DTType.MARSH:
                numPoints = min( numPoints, int( numPoints * self.decorMarshPercentage ) )

            if numPoints > 0:
                # Select the draw functions based on the weights
                decorObjectTypes = random.choices( self.dtDrawDataForType[ self.dtTypes[dt] ][0], weights=self.dtDrawDataForType[ self.dtTypes[dt] ][1], k=numPoints )
            
            for pointIndex in range( numPoints ):
                decorObjectType = decorObjectTypes[ pointIndex ]
                point = self.decorPointsForDts[ dt ][ pointIndex ]

                size = 0
                colour = WHITE
                colourVariance = 0
                drawFcn = None
                
                if decorObjectType == Woodland.DecorObjectType.TREE:
                    drawFcn = Woodland.drawTree
                    # We have a difference between marsh and forest trees
                    if self.dtTypes[dt] == DTType.MARSH:
                        size = random.randint( self.marshTreeMinSize, self.marshTreeMaxSize )
                        colour = MARSH_GREEN
                        colourVariance = self.marshColourVariance
                    else:
                        size = random.randint( self.treeMinSize, self.treeMaxSize )
                        colour = DARK_GREEN
                        colourVariance = self.treeColourVariance
                elif decorObjectType == Woodland.DecorObjectType.PINE:
                    drawFcn = Woodland.drawPine
                    size = random.randint( self.pineMinSize, self.pineMaxSize )
                    colour = DARK_GREEN
                    colourVariance = self.pineColourVariance
                elif decorObjectType == Woodland.DecorObjectType.MOUNTAIN:
                    drawFcn = Woodland.drawMountain
                    size = random.randint( self.mountainMinSize, self.mountainMaxSize )
                    colour = LIGHT_GREY
                    colourVariance = self.mountainColourVariance
                elif decorObjectType == Woodland.DecorObjectType.BUSH:
                    drawFcn = Woodland.drawBush
                    size = random.randint( self.bushMinSize, self.bushMaxSize )
                    colour = DARK_GREEN
                    colourVariance = self.bushColourVariance
                
                colour = np.array( colour )
                # Keep the colour inside the bound of 0 to 255
                for colourIndex in range( len( colour ) ):
                    t = random.randint( colour[ colourIndex ] - colourVariance, colour[ colourIndex ] + colourVariance )
                    t = min( 255, max( t, 0 ) )
                    colour[ colourIndex ] = t
                
                # If theres nothing to draw don't bother adding it
                if drawFcn:
                    data = [ point[0], size, colour, drawFcn ]
                    i, j = self.getDrawGridIndexes( point[0], point[1] )

                    self.drawGridData[j].append( data )


    # Note that this function doesn't return an x, y coordinate in world space, it returns an i, j coordinate in draw grid space because that's what we need later.
    def getDecorIndexesAroundClearing( self, clearing, n ):
        allPoints = []
        cellsFromClearing = int( clearing.rad / self.drawGridCellSize )
        cellsFromClearingSq = cellsFromClearing * cellsFromClearing

        i, j = self.getDrawGridIndexes( clearing.pos[0], clearing.pos[1] )
        minX = int( max( 0, i - cellsFromClearing ) )
        maxX = int( min( self.drawGridSize[0], i + cellsFromClearing + 1 ) )
        minY = int( max( 0, j - cellsFromClearing ) )
        maxY = int( min( self.drawGridSize[1], j + cellsFromClearing + 1 ) )
        
        for x in range( minX, maxX ):
            for y in range( minY, maxY ):
                if self.drawGridOpenCells[x][y] and distSq( np.array([i, j]), np.array([x, y]) ) <= cellsFromClearingSq:
                    allPoints.append( [x, y] )

        n = min( len( allPoints ), n )
        
        decorPoints = random.choices( allPoints, k=n )
        return decorPoints
    
    def generateClearingDecor( self ):
        for clearing in self.clearings:
            decorIndexes = self.getDecorIndexesAroundClearing( clearing, 4 )
            
            for decorIndex in decorIndexes:
                x = self.pos[0] + self.drawGridCellSize * decorIndex[0]
                data = [ x, self.smallHouseSize, WHITE, Woodland.drawSmallHouse ]
                self.drawGridData[decorIndex[1]].append( data )

    def generateLandmarks( self ):
        self.landmarks = []

        if not self.enableLandmarks:
            return
        
        numLandmarksToSpawn = random.randrange( self.minLandmarks, self.maxLandmarks + 1 )
        numLandmarks = len( LandmarkType )
        
        numLandmarksToSpawn = min( numLandmarks, numLandmarksToSpawn )

        # Pick random tris to spawn the landmarks in
        triIndexes = list( range( len( self.tri.simplices ) ) )
        random.shuffle( triIndexes )

        usedTris = [ False for i in range( len( self.tri.simplices ) ) ]

        # Shuffle the landmarks that get spawned
        allLandmarks = list( LandmarkType )
        random.shuffle( allLandmarks )
        
        landmarkIndex = 0
        numSpawnedLandmarks = 0

        # Loop through our list of landmarks and try to spawn them
        while ( landmarkIndex < numLandmarks and numSpawnedLandmarks < numLandmarksToSpawn ):
            landmarkType = allLandmarks[ landmarkIndex ]

            foundSpawn = False
            triListIndex = 0
            while ( not foundSpawn and triListIndex < len( self.tri.simplices ) ):
                triIndex = triIndexes[ triListIndex ]
                landmarkTypesForTri = self.landmarkLookupTable[ self.dtTypes[ triIndex ] ]
                if not usedTris[ triIndex ] and landmarkType in landmarkTypesForTri:
                    foundSpawn = True
                    usedTris[ triIndex ] = True
                else:
                    triListIndex += 1

            if foundSpawn:
                triIndex = triIndexes[ triListIndex ]
                spawnPos = np.array([0.0, 0.0])
                dt = self.tri.simplices[triIndex]
                for pointIndex in dt:
                    spawnPos += self.tri.points[pointIndex]

                spawnPos /= 3
                
                newLandmark = None
                match landmarkType:
                    case LandmarkType.RUIN:
                        newLandmark = Ruin( spawnPos )
                    case LandmarkType.GREATTREE:
                        newLandmark = GreatTree( spawnPos )
                    case LandmarkType.SHIPWRECK:
                        newLandmark = Shipwreck( spawnPos )
                    case LandmarkType.CAVE:
                        newLandmark = Cave( spawnPos )
                    case LandmarkType.VOLCANO:
                        newLandmark = Volcano( spawnPos )
                    case LandmarkType.BEAR:
                        newLandmark = Bear( spawnPos )
                    case LandmarkType.ELK:
                        newLandmark = Elk( spawnPos )
                    case LandmarkType.SHRINE:
                        newLandmark = Shrine( spawnPos )
                    case _:
                        newLandmark = Ruin( spawnPos )

                self.landmarks.append( newLandmark )
                numSpawnedLandmarks += 1
            # Try the next landmark
            landmarkIndex += 1
    
    def nameClearing( self, clearing ):
        potentialNames = []
        potentialNames += self.basicNames
        
        if clearing.hasFeature("River"):
            potentialNames += self.riverNames
        if clearing.hasFeature("Lake"):
            potentialNames += self.lakeNames
        if clearing.hasFeature("Mountain"):
            potentialNames += self.mountainNames
        if clearing.hasFeature("Lake") and clearing.hasFeature("River"):
            potentialNames += self.riverLakeNames
        if clearing.hasFeature("Marsh"):
            potentialNames += self.marshNames

        potentialNamesFiltered = []

        duplicateNames = {}
        
        # Find any unused names, filter out duplicates
        for name in potentialNames:
            # Check if its being used by another clearing
            if not self.allNames[name] and not name in duplicateNames:
                potentialNamesFiltered.append(name)
                duplicateNames[name] = True
        
        if len( potentialNamesFiltered ) > 0:
            name = random.choice( potentialNamesFiltered )
            self.allNames[name] = True
            clearing.name = name

    def generateClearingLocalData( self ):
        for clearing in self.clearings:
            clearing.generateLocalData()

    
    def generateClearingNames( self ):
        for clearing in self.clearings:
            self.nameClearing( clearing )

    
    def generateClearings( self, numClearings ):
        self.clearings = []
        maxPerResidentType = int( numClearings / len( self.residentsTable ) )

        # If we have a non divisible number of clearings then we need to allow for some extras
        if numClearings % len( self.residentsTable ) != 0:
            maxPerResidentType += 1

        residentsList = []
        
        for i in range( maxPerResidentType ):
            for resident in self.residentsTable:
                residentsList.append( resident )

        gridWidth = self.woodlandRight - self.woodlandLeft
        gridHeight = self.woodlandTop - self.woodlandBottom
        
        gridX = int( gridWidth / self.gridSize )
        gridY = int( gridHeight / self.gridSize )
        gridN = gridX * gridY

        useablePoints = [ [ True for _ in range( gridY ) ] for _ in range( gridX ) ]
        # The spaces around the clearing we have to check and clear from useable points
        gridSpacesToClear = int( math.sqrt( self.minClearingDistSq ) / self.gridSize )
        
        numSpawnedClearings = 0
        pointIndex = 0

        possiblePoints = []
        for x in range( gridX ):
            for y in range( gridY ):
                possiblePoints.append( ( x, y ) )
        random.shuffle( possiblePoints )

        while ( numSpawnedClearings < numClearings and pointIndex < gridN ):
            pointToTry = possiblePoints[pointIndex]

            if useablePoints[ pointToTry[0] ][ pointToTry[1] ]:
                # Spawn in the middle of the cell
                newPos = np.array( [ self.woodlandLeft + pointToTry[0] * self.gridSize + self.gridSize / 2.0,
                           self.woodlandBottom + pointToTry[1] * self.gridSize + self.gridSize / 2.0 ] )

                clearing = Clearing( newPos )

                clearing.residents = residentsList[numSpawnedClearings]
                clearing.avail_paths = self.pathsTable[ rollDie(6, 2) ]
            
                clearing.id = numSpawnedClearings
                self.clearings.append(clearing)

                debug_print("Generating clearing "+str(clearing.id))
                debug_print("  Avail_paths: "+str(clearing.avail_paths))

                minX = max( 0, pointToTry[0] - gridSpacesToClear )
                maxX = min( gridX, pointToTry[0] + gridSpacesToClear + 1 )
                minY = max( 0, pointToTry[1] - gridSpacesToClear )
                maxY = min( gridY, pointToTry[1] + gridSpacesToClear + 1 )

                # Clear as useable any points at a far enough distance from this one
                for x in range( minX, maxX ):
                    for y in range( minY, maxY ):
                        # No point doing another distance check if we already ruled this one out
                        if useablePoints[x][y]:
                            otherPos = np.array( [ self.woodlandLeft + x * self.gridSize + self.gridSize / 2.0,
                                         self.woodlandBottom + y * self.gridSize + self.gridSize / 2.0 ] )

                            if distSq( otherPos, newPos ) < self.minClearingDistSq:
                                useablePoints[x][y] = False

                numSpawnedClearings += 1

            # Try the next point always
            pointIndex += 1
        
    def generateBorderPoints( self, numPointsOnEdge ):
        # Get all the corners
        points = [ (self.left, self.bottom), (self.left, self.top), (self.right, self.bottom), (self.right, self.top) ]
        heightRange = ( self.top - self.bottom ) / float( numPointsOnEdge + 1 )
        widthRange = ( self.right - self.left ) / float( numPointsOnEdge + 1 )

        for i in range( numPointsOnEdge ):
            newPoints = [ ( self.left + widthRange * ( i + 1 ), self.bottom ),
                          ( self.left + widthRange * ( i + 1 ), self.top ),
                          ( self.left, self.bottom + heightRange * ( i + 1 ) ),
                          ( self.right, self.bottom + heightRange * ( i + 1 ) ) ]

            points += newPoints 

        return points

    def generateTriData( self ):
        points = [ x.pos for x in self.clearings ]
        points += self.generateBorderPoints( self.numBorderPoints )
        
        npPoints = np.array( points )
        self.tri = Delaunay( npPoints )

        # By default every triangle will be classified a forest
        self.dtTypes = [DTType.FOREST for i in range( len( self.tri.simplices ) )]
        self.isLakeTri = [False for i in range( len( self.tri.simplices ) )]
            
    def generatePaths( self ):
        self.paths = []
        unconnected_clearings = self.clearings.copy()
        
        for i in range(len(self.clearings)):
            # Try paths starting with the point that has the most connections left so we get a better looking graph
            unconnected_clearings.sort(key=lambda x:x.avail_paths, reverse=True)
            
            clearing = unconnected_clearings[0]
            unconnected_clearings.pop(0)
            
            n_indices = (self.tri.vertex_neighbor_vertices[0][clearing.id], self.tri.vertex_neighbor_vertices[0][clearing.id+1])
            neighbours = self.tri.vertex_neighbor_vertices[1][n_indices[0]:n_indices[1]]
            
            other_clearings = [x for x in unconnected_clearings if x.id in neighbours]
            other_clearings.sort( key=lambda x:distSq( x.pos, clearing.pos ) )

            other_index = 0
            while ( clearing.avail_paths > 0 and other_index < len( other_clearings ) ):
                other = other_clearings[ other_index ]
                if ( other.avail_paths > 0 and not clearing.isConnectedTo( other.id ) ):
                    newPath = Path( clearing, other )
                    self.paths.append( newPath )
                    clearing.connected.append( other )
                    other.connected.append( clearing )
                    clearing.avail_paths -= 1
                    other.avail_paths -= 1

                other_index += 1
        
        # it's possible that we've created two separate graphs that aren't linked. Fix that now
        # Find the unions of all the clearings
        unions = [i for i in range(len(self.clearings))]
        for clearing in self.clearings:
            for other in clearing.connected:
                union = min( unions[clearing.id], unions[other.id] )
                unions[clearing.id] = union
                unions[other.id] = union
        # Simplify the unions
        for i in range(len(unions)):
            x = i
            while ( x != unions[x] ):
                x = unions[x]
            unions[i] = x
        
        # Generate the groups
        groups = {}
        for i in range(len(unions)):
            if unions[i] in groups:
                groups[unions[i]].append(self.clearings[i])
            else:
                groups[unions[i]] = [self.clearings[i]]

        # We're going to try every connection and find the best one.
        # This is slower than just finding a good connection and running with it, but since we have only 12 nodes it's worth it to make the graphs look good
        while( len(groups) > 1 ):
            group_keys = list(groups.keys())
            bestClearings = []
            bestDistSq = 1000000 # Just getting a big number here
            newGroupIndex = 0
            # Find the best link to get the first group linked to some other one. Eventually they'll all be linked
            for clearing in groups[group_keys[0]]:
                for other_i in group_keys[1:]:
                    for other in groups[other_i]:
                        newDistSq = distSq( clearing.pos, other.pos )
                        if ( newDistSq < bestDistSq ):
                            bestClearings = [ clearing, other ]
                            bestDistSq = newDistSq

                            newGroupIndex = other_i

            # Unlikely to hit this but just in case don't while loop forever               
            if ( newGroupIndex == 0 ):
                debug_print( "Failed to link the two groups" )
                return
            # Make the link then update the groups
            self.paths.append( Path( bestClearings[0], bestClearings[1] ) )
            bestClearings[0].connected.append( bestClearings[1] )
            bestClearings[1].connected.append( bestClearings[0] )

            groups[newGroupIndex] += groups[group_keys[0]]
            del groups[group_keys[0]]

    def calcCorners( self ):
        # Weigh the edges based on distance from center in each direction to get the corner
        # BR, BL, TR, TL
        self.corners = [ None for i in range(4) ]
        bestCornerScores = [ - self.size[0] - self.size[1] for i in range(4) ]
        cornerScores = [ [ 0 for i in range(4) ] for j in range( len( self.clearings ) ) ]
        center = ( self.left +  0.5 * self.size[0], self.bottom + 0.5 * self.size[1] )
        
        for i in range( len( self.clearings ) ):
            clearing = self.clearings[i]
            cornerScores[i][0] = (center[0] - clearing.pos[0]) + (center[1] - clearing.pos[1])
            cornerScores[i][1] = (clearing.pos[0] - center[0]) + (center[1] - clearing.pos[1])
            cornerScores[i][2] = (center[0] - clearing.pos[0]) + (clearing.pos[1] - center[1])
            cornerScores[i][3] = (clearing.pos[0] - center[0]) + (clearing.pos[1] - center[1])
        
        for c in range( len( self.corners ) ):
            bestCornerIndex = 0
            for i in range( len( self.clearings ) ):
                if cornerScores[i][c] >= bestCornerScores[c]:
                    bestCornerScores[c] = cornerScores[i][c]
                    self.corners[c] = self.clearings[i]
                    bestCornerIndex = i
            # Prevent clearings from being selected as the best for two different corners
            for other_c in range( len( self.corners ) ):
                if other_c != c:
                    cornerScores[bestCornerIndex][other_c] = - self.size[0] - self.size[1]

    def generateLake( self ):
        lakeTris = [ random.randint( 0, len( self.tri.simplices ) - 1 ) ]
        visited = [ False for i in range( len( self.tri.simplices ) ) ]

        # Scale some of the factors we use in the lake generation by how many clearings we have
        numClearings = len( self.clearings )
        
        minLakeClearings = Water.minLakeClearings
        maxLakeClearings = self.scaleByExpectedClearings( Water.maxLakeClearings, Water.minLakeClearings )
        
        numClearings = len( self.clearings )
        lakeClearings = []
        pathsToDestroy = []

        visited[lakeTris[0]] = True
        
        for pointId in self.tri.simplices[lakeTris[0]]:
            if pointId < numClearings:
                lakeClearings.append( self.clearings[pointId] )
                
        # Keep track of possible neighbours
        possibleNeighbours = []

        for lakeTri in lakeTris:
            currNeighbours = self.tri.neighbors[ lakeTri ]
            for currNeighbour in currNeighbours:
                if ( currNeighbour != -1 and not visited[ currNeighbour ] ):
                    possibleNeighbours.append( currNeighbour )
                    visited[currNeighbour] = True
        
        currMaxClearings = maxLakeClearings

        while ( len( possibleNeighbours ) > 0 ):
            # Just check if we can stop adding clearings
            if ( len( lakeClearings ) >= minLakeClearings ):
                roll = rollDie( 6, 2 ) - len( lakeClearings )
                if ( roll < 7 ):
                    currMaxClearings = len( lakeClearings )
            
            nextPossibleNeighbours = []
            
            for neighbour in possibleNeighbours:
                # Find the indexes of every other triangle we would be connecting to 
                existingLakeTriConnections = [ x for x in self.tri.neighbors[ neighbour ] if x in lakeTris ]
                
                if ( self.isGoodLakeConnection( neighbour, existingLakeTriConnections, lakeClearings, pathsToDestroy, currMaxClearings ) ):
                    lakeTris.append( neighbour )
                    newNeighbours = [ x for x in self.tri.neighbors[ neighbour ] if x != -1 and not visited[ x ] ]
                    
                    nextPossibleNeighbours += newNeighbours
                    for newNeighbour in newNeighbours:
                        visited[newNeighbour] = True

            possibleNeighbours = nextPossibleNeighbours

        self.isLakeTri = [False for i in range( len( self.tri.simplices ) )]
        
        # Classify the decor type of these triangles as lake
        for lakeTri in lakeTris:
            self.dtTypes[lakeTri] = DTType.LAKE
            self.isLakeTri[lakeTri] = True
            
        self.lakeTris = lakeTris
        self.lakeClearings = lakeClearings
        for clearing in lakeClearings:
            clearing.addFeature( "Lake" )   
        

    def isGoodLakeConnection( self, neighbour, existingLakeTriConnections, lakeClearings, pathsToDestroy, currMaxClearings ):
        debug_print("Trying to connect " + str(neighbour) + " to lake")

        numClearings = len( self.clearings )
        addedClearings = []
        destroyedPathPoints = []
        pathsToRemoveFromEachClearing = [ 0 for i in range(numClearings) ]
        lakeClearingsToAdd = []

        for existingLakeTriConnection in existingLakeTriConnections:
            # From here check if we would be deleting any paths 
            connectingPoints = [ x for x in self.tri.simplices[neighbour] if x in self.tri.simplices[existingLakeTriConnection] ]
            
            # If there are clearings at these points and they're connected
            if ( connectingPoints[0] < numClearings and connectingPoints[1] < numClearings and self.clearings[connectingPoints[0]].isConnectedTo( connectingPoints[1] ) ):
                destroyedPathPoints.append( ( connectingPoints[0], connectingPoints[1] ) )
                pathsToRemoveFromEachClearing[connectingPoints[0]] += 1
                pathsToRemoveFromEachClearing[connectingPoints[1]] += 1

            if ( self.tri.simplices[neighbour][0] < numClearings ):
                clearing = self.clearings[ self.tri.simplices[neighbour][0] ]
                if clearing not in lakeClearings and clearing not in lakeClearingsToAdd:
                    lakeClearingsToAdd.append( clearing )

            if ( self.tri.simplices[neighbour][1] < numClearings ):
                clearing = self.clearings[ self.tri.simplices[neighbour][1] ]
                if clearing not in lakeClearings and clearing not in lakeClearingsToAdd:
                    lakeClearingsToAdd.append( clearing )

            if ( self.tri.simplices[neighbour][2] < numClearings ):
                clearing = self.clearings[ self.tri.simplices[neighbour][2] ]
                if clearing not in lakeClearings and clearing not in lakeClearingsToAdd:
                    lakeClearingsToAdd.append( clearing )

        validAddition = True

        # If this addition doesn't add any clearings lets give it a random chance to be added
        if ( len( lakeClearingsToAdd ) == 0 ):
            chance = random.random()
            if ( chance > Water.lakeEdgeAddChance ):
                return False

        maxDestroyablePaths = self.scaleByExpectedClearings( Water.maxDestroyablePaths )
        
        if ( len( pathsToDestroy ) + len( destroyedPathPoints ) <= maxDestroyablePaths and len( lakeClearingsToAdd ) + len( lakeClearings ) <= currMaxClearings ):
            for i in range(numClearings):
                if ( len( self.clearings[i].connected ) <= pathsToRemoveFromEachClearing[i] ):
                    return False
        else:
            return False

        if ( validAddition ):
            for pathPoints in destroyedPathPoints:
                # Ensure clearing 1 is the lower value clearing so the removes go okay
                clearing1 = self.clearings[min(pathPoints)]
                clearing2 = self.clearings[max(pathPoints)]

                # Do this long statement so we dont have to do an is in and a remove which is just iterating the list twice over
                clearing1.connected = [ x for x in clearing1.connected if x is not clearing2 ]
                clearing2.connected = [ x for x in clearing2.connected if x is not clearing1 ]

                for path in self.paths:
                    if ( ( path.clearing1 == clearing1 and path.clearing2 == clearing2 ) or ( path.clearing1 == clearing2 and path.clearing2 == clearing1 ) ):
                        self.paths.remove( path )
                        break

            pathsToDestroy += destroyedPathPoints
            lakeClearings += lakeClearingsToAdd

        return validAddition

    def getRandomBorderPoint( self, side ):
        if side == "top":
            return ( random.randint( int( self.left ), int( self.right ) ), int( self.top ) )
        elif side == "bottom":
            return ( random.randint( int( self.left ), int( self.right ) ), int( self.bottom ) )
        elif side == "left":
            return ( int( self.left ), random.randint( int( self.bottom ), int( self.top ) ) )
        elif side == "right":
            return ( int( self.right ), random.randint( int( self.bottom ), int( self.top ) ) )
    
    def generateRiver( self ):
        startPoint = (0, 0)
        endPoint = (0, 0)
        startSide = ""
        endSide = ""

        edgeNames           = [ "top", "bottom", "left", "right" ]
        oppositeEdgeNames   = [ "bottom", "top", "right", "left" ]
        riverPoints = []

        # If we have a lake, then one edge will be attached to the lake
        if len( self.lakeTris ) > 0:
            lakeCentroid = np.array([0.0, 0.0])
            for index in self.lakeTris:
                dt = self.tri.simplices[index]
                for pointIndex in dt:
                    lakeCentroid += self.tri.points[pointIndex]

            lakeCentroid /= ( len( self.lakeTris ) * 3 )

            # Now we need to find the edge that's furthest away from the lake
            edgePoints = [ ( ( self.right - self.left ) / 2.0, self.top ),
                           ( ( self.right - self.left ) / 2.0, self.bottom ),
                           ( self.left, ( self.top - self.bottom ) / 2.0 ),
                           ( self.right, ( self.top - self.bottom ) / 2.0 ) ]

            furthestEdgeIndex = 0
            furthestEdgeDistSq = 0

            for i in range( len( edgePoints ) ):
                distToEdgeSq = distSq( edgePoints[i], lakeCentroid )
                if distToEdgeSq > furthestEdgeDistSq:
                    furthestEdgeIndex = i
                    furthestEdgeDistSq = distToEdgeSq
                    
            endSide = edgeNames[furthestEdgeIndex]
            startSide = oppositeEdgeNames[furthestEdgeIndex]
            endPoint = np.array( self.getRandomBorderPoint( endSide ) )

            # Find the clearing thats on the
            bestStartDistance = self.size[0] * self.size[0]
            bestClearingIndex = None
            for clearing in self.lakeClearings:
                dist = 0
                if endSide == "top" or endSide == "bottom":
                    dist = abs( endPoint[1] - clearing.pos[1] )
                elif endSide == "left" or endSide == "right":
                    dist = abs( endPoint[0] - clearing.pos[0] )

                if dist < bestStartDistance:
                    bestStartDistance = dist
                    startPoint = clearing.pos
                    bestClearing = clearing

            bestClearing.addFeature( "River" )
            riverPoints.append( startPoint )
        # If there is no lake, just pick 2 random edges 
        else:
            startIndex = random.randint(0, 3)
            startSide = edgeNames[startIndex] 
            endSide = oppositeEdgeNames[startIndex]

            startPoint = np.array( self.getRandomBorderPoint( startSide ) )
            endPoint = np.array( self.getRandomBorderPoint( endSide ) )
            riverPoints.append(startPoint)

        possPoints = []
        possClearings = []
        for clearing in self.clearings:
            if not clearing.hasFeature( "Lake" ):
                # If we have a lake make sure we didn't pick any points past the bounds
                if len( self.lakeTris ) > 0:
                    pt = clearing.pos
                    # Clear points that aren't in range
                    if startSide == "top" and pt[1] > startPoint[1]:
                        continue
                    if startSide == "bottom" and pt[1] < startPoint[1]:
                        continue
                    if startSide == "left" and pt[0] < startPoint[1]:
                        continue
                    if startSide == "right" and pt[0] > startPoint[1]:
                        continue
                
                possPoints.append( clearing.pos )
                possClearings.append( clearing )

        numPossClearings = len( possClearings )

        for i in range( len( self.tri.simplices ) ):
            if not self.isLakeTri[i]:
                dt = self.tri.simplices[i]
                centroid = np.array([0.0, 0.0])
                for pointIndex in dt:
                    centroid += self.tri.points[pointIndex]
                    
                centroid /= 3

                # If we have a lake make sure we didn't pick any points past the bounds
                if len( self.lakeTris ) > 0:
                    # Clear points that aren't in range
                    if startSide == "top" and centroid[1] > startPoint[1]:
                        continue
                    if startSide == "bottom" and centroid[1] < startPoint[1]:
                        continue
                    if startSide == "left" and centroid[0] < startPoint[0]:
                        continue
                    if startSide == "right" and centroid[0] > startPoint[0]:
                        continue
                
                possPoints.append( centroid )
        
        possPoints.append(endPoint)
        lastPoint = riverPoints[-1]
        nextPointIndex = -1
        numPossPoints = len( possPoints )
        inRiver = [False for i in range( numPossPoints )]
        pointIndexes = []
        lastClearing = None
        
        while ( nextPointIndex != numPossPoints - 1 ):
            smallestDistSq = self.size[0] * self.size[0]

            for i in range( numPossPoints ):
                point = possPoints[i]
                if not inRiver[i]:
                    # Make sure we're going in the right direction
                    if ( ( startSide == "top" and lastPoint[1] > point[1] ) or
                         ( startSide == "bottom" and lastPoint[1] < point[1] ) or
                         ( startSide == "left" and lastPoint[0] < point[0] ) or
                         ( startSide == "right" and lastPoint[0] > point[0] ) ):
                        distToPointSq = self.riverCloseWeight * distSq( lastPoint, point ) + self.riverFarWeight * distSq( point, endPoint )
                        # We want to consider clearings stronger than normal points
                        if ( i < numPossClearings ):
                            distToPointSq *= self.riverClearingFactor

                            # Give less consideration to clearings connected by a path to this one already
                            if lastClearing and possClearings[i] in lastClearing.connected:
                                distToPointSq *= self.riverConnectedFactor
                                
                        if ( distToPointSq < smallestDistSq ):
                            smallestDistSq = distToPointSq
                            nextPointIndex = i

            inRiver[ nextPointIndex ] = True
            pointIndexes.append( nextPointIndex )
            lastPoint = possPoints[ nextPointIndex ]

            if nextPointIndex < numPossClearings:
                lastClearing = possClearings[nextPointIndex]
        
        for pointIndex in pointIndexes:
            if pointIndex < numPossClearings:
                possClearings[pointIndex].addFeature( "River" )
            riverPoints.append( possPoints[pointIndex] )

        self.riverControlPoints = riverPoints

        # interpolate the spline
        xs = [i[0] for i in riverPoints]
        ys = [i[1] for i in riverPoints]

        k = min( 3, len( riverPoints ) - 1 )
        tck, u = intp.splprep( [xs, ys], s=1, k=k )
        uNew = np.arange(0, 1.01, 0.05)
        out = intp.splev( uNew, tck )

        self.riverSplinePoints = [(out[0][i], out[1][i]) for i in range( len( out[0] ) )]

        numRiverSplinePoints = len( self.riverSplinePoints )
        self.riverHullPoints = [(0,0) for _ in range( 2 * numRiverSplinePoints )]
        prevRiverLeftWidth = self.riverWidthMin + ( self.riverWidthMax - self.riverWidthMin ) / 2
        prevRiverRightWidth = prevRiverLeftWidth
                        
        for riverIndex in range( numRiverSplinePoints ):
            # For each pair of river points, calculate the forward and space it outwards in both directions
            riverPoint = self.riverSplinePoints[riverIndex]
            fwd = np.array([0,0])
            if riverIndex < numRiverSplinePoints - 1:
                fwd = np.array(self.riverSplinePoints[riverIndex + 1]) - np.array(self.riverSplinePoints[riverIndex])
            # For the last point we want to project it off the map so the smoothing doesn't visibly cut it off
            else:
                fwd = np.array(self.riverSplinePoints[riverIndex]) - np.array(self.riverSplinePoints[riverIndex - 1])
                riverPoint += fwd

            fwd /= np.linalg.norm( fwd )
            left = np.array([ -fwd[1], fwd[0] ])
            right = np.array([ fwd[1], -fwd[0] ])

            leftWidth = prevRiverLeftWidth + np.random.normal() * self.riverWidthVariance
            rightWidth = prevRiverRightWidth + np.random.normal() * self.riverWidthVariance

            leftWidth = min( max( self.riverWidthMin, leftWidth ), self.riverWidthMax )
            rightWidth = min( max( self.riverWidthMin, rightWidth ), self.riverWidthMax )
            
            leftRiverPoint = riverPoint + leftWidth * left
            rightRiverPoint = riverPoint + rightWidth * right

            self.riverHullPoints[riverIndex] = leftRiverPoint
            self.riverHullPoints[-(riverIndex+1)] = rightRiverPoint

    def getIntersectionPoint( self, p1, p2, q1, q2 ):
        a = p1[0]*p2[1] - p1[1]*p2[0]
        b = q1[0]*q2[1] - q1[1]*q2[0]
        c = float( ( p1[0] - p2[0] ) * ( q1[1] - q2[1] ) - ( p1[1] - p2[1] ) * ( q1[0] - q2[0] ) )

        x = ( a * ( q1[0] - q2[0] ) - b * ( p1[0] - p2[0] ) ) / c
        y = ( a * ( q1[1] - q2[1] ) - b * ( p1[1] - p2[1] ) ) / c

        return np.array([x, y])
        
    
    def generateBridges( self ):
        # Find anywhere that the river intersects a path
        for i in range( len( self.riverSplinePoints ) - 1 ):
            p1 = np.array(self.riverSplinePoints[i])
            p2 = np.array(self.riverSplinePoints[i+1])
            
            for path in self.paths:
                if path.intersects(p1, p2):
                    intersect = self.getIntersectionPoint( p1, p2, path.clearing1.pos, path.clearing2.pos )
                    fwd = p2 - p1
                    fwd /= np.linalg.norm( fwd )
                    left = np.array([ -fwd[1], fwd[0] ])

                    self.bridges.append( [ intersect + self.bridgeHalfSize * left + self.bridgeHalfWidth * fwd,
                                           intersect - self.bridgeHalfSize * left + self.bridgeHalfWidth * fwd,
                                           intersect - self.bridgeHalfSize * left - self.bridgeHalfWidth * fwd,
                                           intersect + self.bridgeHalfSize * left - self.bridgeHalfWidth * fwd ] )
                    
            
    def generateWater( self ):
        self.water = None
        self.lakeClearings = []
        self.lakeTris = []
        self.riverSplinePoints = []
        self.riverControlPoints = []
        self.riverHullPoints = []
        self.bridges = []
        
        chance = rollDie( 6, 1 )
        
        if self.forceLake or ( self.enableLake and chance > 3 ):
            self.generateLake()

        if self.forceRiver or ( self.enableRiver and chance < 5 ):
            self.generateRiver()
            self.generateBridges()

        if len( self.lakeTris ) > 0 or len( self.riverHullPoints ) > 0:
            self.water = Water( self.lakeTris, self.riverHullPoints, self )
        
    def generateWoodlandControl( self ):
        marquisateCorner = random.randint(0, 3)
        if self.enableMarquisate:
            self.generateMarquisateControl( self.corners[marquisateCorner] )

        eyrieCorner = self.oppositeCorners[ marquisateCorner ]
        if self.enableEyrie:
            self.generateEyrieControl( self.corners[eyrieCorner] )

        if self.enableWoodlandAlliance:
            self.generateWoodlandAllianceControl()

        otherCorners = []
        for i in range(len(self.corners)):
            if ( i != marquisateCorner and i != eyrieCorner ):
                otherCorners.append(i)
                
        lizardCultCorner = random.sample( otherCorners, 1 )[0]
        grandDuchyCorner = self.oppositeCorners[ lizardCultCorner ]

        if self.enableLizardCult:
            self.generateLizardCultControl( self.corners[ lizardCultCorner ] )
        if self.enableRiverfolk:
            self.generateRiverfolkControl()
        if self.enableDuchy:
            self.generateGrandDuchyControl( self.corners[ grandDuchyCorner ] )
        if self.enableCorvids:
            self.generateCorvidConspiracyControl()

    def generateMarquisateControl( self, corner ):
        corner.control = "Marquisate"
        corner.addFeature( "Stronghold" )
        depths = self.getDepthFrom( corner )

        for clearing in self.clearings:
            if clearing.id != corner.id:
                controlRoll = rollDie( 6, 2 )
                if depths[ clearing.id] < len( self.marquisateControlVals ) and controlRoll >= self.marquisateControlVals[ depths[ clearing.id ] ]:
                    clearing.control = "Marquisate"

    def generateEyrieControl( self, corner ):
        corner.control = "Eyrie"
        corner.addFeature( "Roost" )
        depths = self.getDepthFrom( corner )

        for clearing in self.clearings:
            if clearing.id != corner.id and not clearing.hasFeature( "Stronghold" ):
                controlRoll = rollDie( 6, 2 )
                if depths[ clearing.id] < len( self.eyrieControlVals ) and controlRoll >= self.eyrieControlVals[ depths[ clearing.id ] ]:
                    if clearing.control == "Marquisate":
                        clearing.addFeature( "Lost Marquisate Control" )
                    clearing.control = "Eyrie"
                if depths[ clearing.id] < len( self.eyrieRoostVals ) and controlRoll >= self.eyrieRoostVals[ depths[ clearing.id ] ]:
                    clearing.addFeature( "Roost" )

    def generateWoodlandAllianceControl( self ):
        for clearing in self.clearings:
            supportRoll = rollDie( 6, 2 )
            sympathy = False
            if clearing.hasFeature( "Lost Marquisate Control" ) and supportRoll >= 8:
                sympathy= True
            elif clearing.control == "None" and supportRoll >= 9:
                sympathy = True
            elif supportRoll >= 11:
                sympathy = True

            if sympathy:
                controlRoll = rollDie( 6, 2 )
                # Get a base and get sympathy in all connected spots
                if controlRoll == 12 and not clearing.hasFeature( "Stronghold" ):
                    clearing.control = "Woodland Alliance"
                    for connected in clearing.connected:
                        if not connected.hasFeature( "Woodland Alliance Support" ):
                            connected.addFeature( "Woodland Alliance Support" )
                    clearing.addFeature( "Base" )
                    clearing.removeFeature( "Woodland Alliance Support" )
                elif controlRoll >= 10 and not clearing.hasFeature( "Stronghold" ):
                    clearing.control = "Woodland Alliance"
                    clearing.addFeature( "Base" )
                    clearing.removeFeature( "Woodland Alliance Support" )
                elif not clearing.hasFeature( "Woodland Alliance Support" ):
                    clearing.addFeature( "Woodland Alliance Support" )

    def generateLizardCultControl( self, corner ):
        outcastIndex = random.randint(0, len( self.residentsTable ) - 1 )
        outcastType = self.residentsTable[ outcastIndex ]

        outcastClearings = []
        for clearing in self.clearings:
            if clearing.residents == outcastType:
                outcastClearings.append( clearing )

        numCultClearings = min( 2, len( outcastClearings ) )
        cultClearings = random.sample( outcastClearings, numCultClearings )

        for clearing in cultClearings:
            clearing.addFeature( "Lizard Cult Support" )

        # Clear out the old stuff in the clearing we're taking over
        if corner.control in self.possibleBuildingLosses:
            for building in self.possibleBuildingLosses[ corner.control ]:
                corner.removeFeature( building )
                
        corner.control = "Lizard Cult"
        corner.addFeature( "Garden" )

    def generateRiverfolkControl( self ):
        clearingIndexes = [i for i in range(len(self.clearings))]
        riverfolkScores = [0 for i in range(len(self.clearings))]

        for i in range(len(self.clearings)):
            clearing = self.clearings[i]
            score = 0
            if ( clearing.hasFeature( "River" ) or clearing.hasFeature( "Lake" ) ):
                score += 1
            if ( len( clearing.connected ) > 2 ):
                score += 1
            if ( len( clearing.connected ) > 3 ):
                score += 1

            for resource in self.riverfolkValuableResources:
                if ( clearing.hasFeature( resource ) ):
                    score += 1
                    break

            if clearing.hasFeature( "Stronghold" ) or clearing.hasFeature( "Roost" ):
                score = 0

            riverfolkScores[i] = score

        # Sort clearings and take the best 4
        clearingIndexes.sort( key=lambda x: riverfolkScores[x], reverse=True )

        numRiverfolk = self.scaleByExpectedClearings( self.nRiverfolkPresences, 1 )
        for i in range( numRiverfolk ):
            clearing = self.clearings[ clearingIndexes[i] ]
            clearing.addFeature( "Riverfolk" )

    def generateGrandDuchyControl( self, corner ):
        # Clear out the old stuff in the clearing we're taking over
        if corner.control in self.possibleBuildingLosses:
            for building in self.possibleBuildingLosses[ corner.control ]:
                corner.removeFeature( building )

        corner.control = "Grand Duchy"
        corner.addFeature( "Tunnel" )

        for clearing in corner.connected:
            if ( not clearing.hasFeature( "Garden" ) and not clearing.hasFeature( "Stronghold" ) ):
                roll = rollDie( 6, 2 )
                if ( roll >= self.duchyControlVal ):
                    # Clear the old features from the clearing being taken over
                    if clearing.control in self.possibleBuildingLosses:
                        for building in self.possibleBuildingLosses[ clearing.control ]:
                            clearing.removeFeature( building )
                    clearing.control = "Grand Duchy"

        nonDuchyClearings = [ clearing for clearing in self.clearings if not clearing.control == "Grand Duchy" ]

        numTunnels = self.scaleByExpectedClearings( 1, 1 )
        numTunnels = min( numTunnels, len( nonDuchyClearings ) )
        randomClearings = random.sample( nonDuchyClearings, numTunnels )

        for clearing in randomClearings:
            clearing.addFeature( "Tunnel" )

    def generateCorvidConspiracyControl( self ):
        numCorvidClearings = self.scaleByExpectedClearings( 4, 1 )
        numCorvidClearings = min( numCorvidClearings, len( self.clearings ) )
        corvidClearings = random.sample( self.clearings, numCorvidClearings )

        for clearing in corvidClearings:
            clearing.addFeature( "Corvid Conspiracy" )
        
    def getDepthFrom( self, clearing ):
        depths = [0 for i in range(len(self.clearings))]
        found = [False for i in range(len(self.clearings))]

        self.getDepthRecursive( clearing, depths, found, 0 )
        return depths
    
    def getDepthRecursive( self, clearing, depths, found, depth ):
        depths[ clearing.id ] = depth
        found[ clearing.id ] = True

        for connected in clearing.connected:
            if not found[ connected.id ]:
                self.getDepthRecursive( connected, depths, found, depth+1)

    def debugWrite(self):
        self.debugWritePaths
        
    def debugWritePaths(self):
        debug_print("All Paths:")
        for path in paths:
            debug_print("  " + str(path.clearing1.id) + " to " + str(path.clearing2.id))
