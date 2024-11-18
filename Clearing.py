from WoodlandCommon import *
from Woodland import *
from Path import *
from Denizen import *

import random
import numpy as np
from scipy.spatial import Delaunay
from scipy import interpolate as intp

class Clearing:
    # Data for drawing
    rad = 20

    # Data for drawing features
    featureSize = 20
    featureSpacing = 2
    outlineWidth = 1
    fortificationHeight = 3

    # These are relative to the origin of the clearing
    # They are ordered by how close they are to the clearing so the drawing looks better
    featureLocations = [ [ -rad - featureSize - featureSpacing, -rad ],
                         [ -rad - featureSize - featureSpacing, -rad + featureSize + featureSpacing ],
                         [ rad + featureSpacing, -rad ],
                         [ rad + featureSpacing, -rad + featureSize + featureSpacing],
                         [ -rad - 2 * ( featureSize + featureSpacing ), -rad ],
                         [ -rad - 2 * ( featureSize + featureSpacing ), -rad + featureSize + featureSpacing ],
                         [ rad + featureSize + 2 * featureSpacing, -rad ],
                         [ rad + featureSize + 2 * featureSpacing, -rad + featureSize + featureSpacing] ]
    maxFeatures = len( featureLocations )

    # Methods for drawing all types of features
    @staticmethod
    def drawStronghold( screen, org, size ):
        points = [ [ 0, 1], [ 1, 1], [ 1, 0.375], [ 0.875, 0.25], [ 0.75, 0.375], [ 0.75, 0.25], [ 0.5, 0], [ 0.25, 0.25], [ 0.25, 0.375], [ 0.125, 0.25], [ 0, 0.375] ]

        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )
            
        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawRoost( screen, org, size ):
        points = [ [0, .2], [.1, .1], [.1, 0], [.3, .1], [.5, 0], [.7, .1], [.9, 0], [.9, .1], [1, .2], [1, .35], [.85, .45], [.85, .55], [.7, .65], [.7, .9], [.8, 1], [.2, 1], [.3, .9], [.3, .65], [.15, .55], [.15, .45], [0, .35]]

        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Eyrie" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawLostMarquisateControl( screen, org, size ):
        points = [ [ 0, 1], [ 1, 1], [ 1, 0.375], [ 0.875, 0.25], [ 0.75, 0.375], [ 0.5, 0.75] ]

        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawWoodlandAllianceSupport( screen, org, size ):
        points = [ [.15, 0], [.3, 0], [.45, .15], [.55, .15], [.7, 0], [.85, 0], [1.0, 0.15], [1.0, .3], [.85, .45], [.85, .7], [.65, .9], [.35, .9], [.15, .7], [.15, .45], [0.0, .3], [.0, .15] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Woodland Alliance" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawWoodlandAllianceBase( screen, org, size ):
        points = [ [0, 0], [0.2, 0], [0.2, 0.2], [.4, .2], [.4, 0], [.6, 0], [.6, .2], [.8, .2], [.8, 0], [1, 0], [1, 1], [0, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Woodland Alliance" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawLizardCultSupport( screen, org, size ):
        points = [ [0, 0.1], [0.25, 0], [.6, 0], [1, .15], [1, .45], [.6, .6], [.7, .9], [.15, .9], [.25, .6], [0.0, .5], [.25, .4], [.0, .3], [.25, .2] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Lizard Cult" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawGarden( screen, org, size ):
        points = [ [0, .8], [0, 0.6], [0.166, 0.3], [.333, 0.6], [.5, .3], [.666, .6], [.833, .3], [1, .6], [1, .8] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Lizard Cult" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawInProgressGarden( screen, org, size ):
        points = [ [0, .8], [0, 0.7], [0.166, 0.6], [.333, 0.7], [.5, .6], [.666, .7], [.833, .6], [1, .7], [1, .8] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Lizard Cult" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawRiverfolk( screen, org, size ):
        points = [ [.1, 0], [.2, 0], [.3, .1], [.7, .1], [.8, 0], [.9, 0], [1.0, 0.1], [1.0, .2], [.9, .3], [.9, .7], [.7, .9], [.3, .9], [.1, .7], [.1, .3], [0.0, .2], [.0, .1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Riverfolk" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawTunnel( screen, org, size ):
        points = [ [0, 0.8], [.2, .4], [.3, .5], [.7, .5], [.8, .4], [1, .8] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Grand Duchy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawCorvidConspiracy( screen, org, size ):
        points = [ [0.1, 1], [0.2, 0.75], [0, 0.5], [0, 0.25], [0.25, 0], [0.5, 0], [0.75, .25], [1, 0.2], [0.75, 0.375], [1, 0.6], [0.75, 0.5], [0.6, .75], [0.7, 1.0] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Corvid Conspiracy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawPlot( screen, org, size ):
        points = [ [0.2, 0.2], [0.4, 0], [.6, 0], [.8, .2], [.8, .8], [.6, 1], [.4, 1], [.2, .8] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Corvid Conspiracy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawTradingPost( screen, org, size ):
        points = [ [0, 0], [1, 0], [1, 1], [0, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Riverfolk" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawCitadel( screen, org, size ):
        points = [ [0, 0], [1, 0], [1, 1], [0, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Grand Duchy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawMarket( screen, org, size ):
        points = [ [0, 1], [.5, 0], [1, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Grand Duchy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawSawmill( screen, org, size ):
        points = [ [0.5, 0], [1, 0.5], [.5, 1], [0, .5] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawWorkshop( screen, org, size ):
        points = [ [0, 0], [1, 0], [1, 1], [0, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawRecruiter( screen, org, size ):
        points = [ [0, 1], [.5, 0], [1, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    # Methods for drawing control icons
    @staticmethod
    def drawMarquisateControl( screen, org, size ):
        points = [ [0, 0], [0.33, 0.25], [.66, .25], [1, 0], [1, .75], [.75, 1], [.25, 1], [0, .75] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Marquisate" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawEyrieControl( screen, org, size ):
        points = [ [0, 1], [0.2, 0.8], [0.1, 0.1], [0.5, 0.3], [0.75, 0.3], [1.0, 0.5], [0.75, .7], [0.75, 0.8], [0.95, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Eyrie" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawWoodlandAllianceControl( screen, org, size ):
        Clearing.drawWoodlandAllianceSupport( screen, org, size )
        
    @staticmethod
    def drawLizardCultControl( screen, org, size ):
        Clearing.drawLizardCultSupport( screen, org, size )

    @staticmethod
    def drawRiverfolkControl( screen, org, size ):
        Clearing.drawRiverfolk( screen, org, size )

    @staticmethod
    def drawGrandDuchyControl( screen, org, size ):
        points = [ [0, 1], [0, 0.64], [0.09, 0.37], [0.21, 0.19], [0.36, 0.1], [0.6, 0.1], [0.7, .3], [1, 0.3], [.8, .5], [.9, 1] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Grand Duchy" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawCorvidControl( screen, org, size ):
        Clearing.drawCorvidConspiracy( screen, org, size )

    # Methods for drawing denizens
    @staticmethod
    def drawFox( screen, org, size ):
        points = [ [0, 0], [0.33, 0.25], [.66, .25], [1, 0], [1, .75], [.5, 1], [0, .75] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Denizens" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawMouse( screen, org, size ):
        points = [ [.15, 0], [.3, 0], [.45, .15], [.55, .15], [.7, 0], [.85, 0], [1.0, 0.15], [1.0, .3], [.85, .45], [.85, .7], [.65, .9], [.35, .9], [.15, .7], [.15, .45], [0.0, .3], [.0, .15] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Denizens" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    @staticmethod
    def drawRabbit( screen, org, size ):
        points = [ [0, 0.05], [0.05, 0], [0.15, 0], [0.5, 0.4], [0.85, 0], [.95, 0], [1, .05], [1, .15], [0.7, 0.35], [0.875, 0.55], [0.875, 0.8], [0.675, 1], [0.325, 1], [0.125, 0.8], [0.125, 0.55], [0.3, 0.35], [0, 0.15] ]
        
        for i in range( len( points ) ):
            points[i] = org + size * np.array( points[i] )

        pygame.draw.polygon( screen, controlColours[ "Denizens" ], points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )

    controlDict = { "Marquisate" : drawMarquisateControl,
                    "Eyrie" : drawEyrieControl,
                    "Woodland Alliance" : drawWoodlandAllianceControl,
                    "Lizard Cult" : drawLizardCultControl,
                    "Riverfolk" : drawRiverfolkControl,
                    "Grand Duchy" : drawGrandDuchyControl,
                    "Corvid Conspiracy" : drawCorvidControl,
                    "Denizens" : drawMouse,
                    "None" : None
                    }

    controlDrawSize = 25
      
    featuresDict = { "Stronghold":                  [ "Marquisate", drawStronghold ],
                     "Roost":                       [ "Eyrie", drawRoost ],
                     "Lost Marquisate Control":     [ "Marquisate", drawLostMarquisateControl ],
                     "Woodland Alliance Support":   [ "Woodland Alliance", drawWoodlandAllianceSupport ],
                     "Base":                        [ "Woodland Alliance", drawWoodlandAllianceBase ],
                     "Lizard Cult Support":         [ "Lizard Cult", drawLizardCultSupport ],
                     "Garden":                      [ "Lizard Cult", drawGarden ],
                     "Riverfolk":                   [ "Riverfolk", drawRiverfolk ],
                     "Tunnel":                      [ "Grand Duchy", drawTunnel ],
                     "Corvid Conspiracy":           [ "Corvid Conspiracy", drawCorvidConspiracy ],
                     "Lake":                        [ "None", None ],
                     "River":                       [ "None", None ],
                     "Fortifications":              [ "None", None ],
                     "Market":                      [ "Grand Duchy", drawMarket ],
                     "Citadel":                     [ "Grand Duchy", drawCitadel ],
                     "Workshop":                    [ "Marquisate", drawWorkshop ],
                     "Sawmill":                     [ "Marquisate", drawSawmill ],
                     "Recruiter":                   [ "Marquisate", drawRecruiter ],
                     "Plot":                        [ "Corvid Conspiracy", drawPlot ],
                     "Trading Post":                [ "Riverfolk", drawTradingPost ],
                     "In Progress Garden":          [ "Lizard Cult", drawInProgressGarden ],
                     "Mountain":                    [ "None", None ],
                     "Marsh":                       [ "None", None ],
                     }

    residentsDict = { "Fox" : drawFox,
                      "Mouse" : drawMouse,
                      "Rabbit" : drawRabbit,
                      "None" : None
                      }
    
    residentsDrawSize = 15

    localInfoDrawSpacing = 1
    
    numDenizens = 2
    numBuildings = 2
    numProblems = 2

    # Don't add the Bridge and Dam buildings here. Those are fleshed out in the map generation process already
    allBuildings = ["Mill", "Forge", "Well", "Farm", "Kiln", "Town Hall", "Guard Tower", "Wall", "Longhouse",
                          "Archive", "Larder", "Grain Silo", "Armory", "Infirmary", "Brewery", "Bakehouse", "Woodshop",
                          "Warehouse", "Orchard", "Custom House", "Market", "Monastery", "Tavern", "Inn", "Almshouse",
                          "Barracks", "Schoolhouse", "Bank", "Fountain", "Prison", "Graveyard", "Courthouse",
                          "Trading Post", "Aqueduct"]

    allProblems = ["Bear", "Natural Disaster", "Bandits", "Enemy Occupation", "Famine", "Sickness", "Tyranny", "War",
                   "Money", "Inequality", "Overpopulation", "Lack of Development", "Corruption", "Dissent",
                   "Lack of Crucial Resource", "Lack of Skilled Labour", "Overtaxation", "Sabotage", "Internal Strife",
                   "Inflexible Traditions", "Prejudice", "Brutality", "Protection Racket", "Xenophobia", "Road Damage",
                   "Obsolescence", "Cultural Assimilation", "Coup", "Poisoned Supplies", "Dilapidated Architecture",
                   "Fearmongering", "Warmongering", "Smugglers", "Thieves", "Censorship", "Unexplained Happenings"]
                   

    statusDescriptions  = ["Untouched", "Affected", "Battle-scarred", "War-torn"]
    statusColours       = [GREEN, YELLOW, ORANGE, RED]
    maxStatus = len( statusDescriptions ) - 1
    statusDecreaseTicks = 6
    
    def __init__( self, pos ):
        self.pos = pos
        self.connected = []
        self.avail_paths = 0
        self.id = 0
        self.residents = "None"
        self.name = "None"
        self.control = "None"
        self.features = []
        self.denizens = []
        self.buildings = []
        self.problems = []
        self.status = 0
        self.ticksSinceLastAttack = 0

    def update( self ):
        self.ticksSinceLastAttack += 1
        if self.status > 0 and self.ticksSinceLastAttack >= self.statusDecreaseTicks:
            self.ticksSinceLastAttack = 0
            self.status -= 1

    def increaseWarStatusBy( self, n ):
        self.status = min( self.maxStatus, self.status + n )
        self.ticksSinceLastAttack = 0

    def generateLocalData( self ):
        # Generate important Denizens
        for i in range( self.numDenizens ):
            denizen = Denizen()
            denizen.generateSpecies( self )
            self.denizens.append( denizen )

        denizenOccupations = random.sample( Denizen.occupations, self.numDenizens )
        for i in range( self.numDenizens ):
            self.denizens[i].occupation = denizenOccupations[i]

        # Generate important buildings (Keeping this separate from features)
        self.buildings = random.sample( self.allBuildings, self.numBuildings )
        
        # Generate problems
        self.problems = random.sample( self.allProblems, self.numProblems )

        # Generate war status
        self.generateWarStatus()

    def generateWarStatus( self ):
        factionsInArea = { self.control: True }
        numFactionsInArea = 1

        for clearing in self.connected:
            if clearing.control not in factionsInArea:
                factionsInArea[clearing.control] = True
                numFactionsInArea += 1

        # All denizens or all uncontrolled should be less war affected
        if self.control == "None" or self.control == "Denizens":
            numFactionsInArea -= 1
            
        warRollBonus = min( 3, numFactionsInArea )
        warRoll = rollDie( 6, 2 ) + warRollBonus

        if warRoll > 12:
            self.status = 3
            if not self.hasFeature( "Fortifications" ):
                self.addFeature( "Fortifications" )
        elif warRoll > 10:
            self.status = 2
        elif warRoll > 7:
            self.status = 1
        else:
            self.status = 0
                 
        
    def draw( self, screen ):
        colour = controlColours[ self.control ]
        
        pygame.draw.circle( screen, WHITE, self.pos, self.rad )
        pygame.draw.circle( screen, self.statusColours[self.status], self.pos, self.rad, 3 )
        
        nameTextSize = font20.size( self.name )
        nameTextPos = [ self.pos[0] - nameTextSize[0] / 2.0, self.pos[1] + self.rad ]

        outlineText( screen, nameTextPos, self.name, font20, WHITE, BLACK )

        controlDrawFcn = self.controlDict[ self.control ]
        if controlDrawFcn != None:
            controlDrawPos = self.pos - np.array( [self.controlDrawSize / 2.0, self.controlDrawSize / 2.0 ] )
            controlDrawFcn( screen, controlDrawPos, self.controlDrawSize )

        residentsDrawFcn = self.residentsDict[ self.residents ]
        if residentsDrawFcn != None:
            residentsDrawPos = [ self.pos[0] + nameTextSize[0] / 2.0, self.pos[1] + self.rad + nameTextSize[1] / 5.0 ]
            residentsDrawFcn( screen, residentsDrawPos, self.residentsDrawSize )

        self.drawFeatures( screen )

    # Fortifications are special, we draw them on top of the circle
    def drawFortifications( self, screen ):
        points = [ [-1, 1], [-1, .5], [-.6, .5], [-.6, .7], [-.2, .7], [-.2, .5], [.2, .5], [.2, .7], [.6, .7], [.6, .5], [1, .5], [1, 1] ]
        
        for i in range( len( points ) ):
            points[i] = self.pos + self.rad * np.array( points[i] )
        
        pygame.draw.polygon( screen, LIGHT_GREY, points )
        pygame.draw.polygon( screen, BLACK, points, width=Clearing.outlineWidth )
    
    def drawFeatures( self, screen ):
        featureLocationIndex = 0
        for featureIndex in range( len( self.features ) ):
            if self.features[ featureIndex ] == "Fortifications":
                self.drawFortifications( screen )
            elif featureLocationIndex < self.maxFeatures:
                data = Clearing.featuresDict[ self.features[ featureIndex ] ]
                control = data[0]
                drawFcn = data[1]
                
                if drawFcn != None:
                    featureLocation = self.featureLocations[ featureLocationIndex ] + self.pos
                    drawFcn( screen, featureLocation, self.featureSize )
                    
                    featureLocationIndex += 1

    def drawLocalInfo( self, screen, pos ):
        texts = [ self.name + ": " + self.residents ]
        fonts = [ basicFont14 ]
        colours = [ BLACK ]

        texts.append( "War status: " + self.statusDescriptions[ self.status ] )
        fonts.append( basicFont12 )
        colours.append( self.statusColours[ self.status ] )
        
        texts.append( "Important Denizens:" )
        fonts.append( basicFont12 )
        colours.append( BLACK )
        for i in range( self.numDenizens ):
            texts.append( " - " + self.denizens[i].name + ": " + self.denizens[i].species + " " + self.denizens[i].occupation )
            fonts.append( basicFont12 )
            colours.append( BLACK )

        texts.append( "Important Buildings:" )
        fonts.append( basicFont12 )
        colours.append( BLACK )
        for i in range( self.numBuildings ):
            texts.append( " - " + self.buildings[i] )
            fonts.append( basicFont12 )
            colours.append( BLACK )

        texts.append( "Problems:" )
        fonts.append( basicFont12 )
        colours.append( BLACK )
        for i in range( self.numProblems ):
            texts.append( " - " + self.problems[i] )
            fonts.append( basicFont12 )
            colours.append( BLACK )
        
        drawTextTable( screen, pos, texts, fonts, colours, self.localInfoDrawSpacing, WHITE, BLACK )
        
    def isConnectedTo( self, id ):
        for clearing in self.connected:
            if ( clearing.id == id ):
                return True
        return False

    def addFeature( self, featureString ):
        if featureString in self.featuresDict:
            self.features.append(featureString)
        else:
            #debug_string("Trying to add nonexistent feature "+featureString+" to clearing "+str(clearing.id))
            return

    def hasFeature( self, featureString ):
        if featureString in self.featuresDict:
            return featureString in self.features
        else:
            #debug_string("Trying to find nonexistent feature "+featureString+" in clearing "+str(clearing.id))
            return False

    def removeFeature( self, featureString ):
        if featureString in self.featuresDict:
            if self.hasFeature( featureString ):
                self.features.remove(featureString)
        else:
            #debug_string("Trying to remove nonexistent feature "+featureString+" to clearing "+str(clearing.id))
            return
