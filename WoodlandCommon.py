import pygame
import random
import math
import numpy as np


"""
GLOBAL SETTINGS ALL FILES NEED TO SEE
"""
class GlobalSettings:
    def __init__( self ):
        self.useClassicGraphics = True

GLOBAL_SETTINGS = GlobalSettings()

"""
FONTS
"""
font24 = pygame.font.SysFont("vinerhanditc", 24)
font20 = pygame.font.SysFont("vinerhanditc", 20)
font18 = pygame.font.SysFont("vinerhanditc", 18)
font16 = pygame.font.SysFont("vinerhanditc", 16)
font14 = pygame.font.SysFont("vinerhanditc", 14)
font12 = pygame.font.SysFont("vinerhanditc", 12)
font10 = pygame.font.SysFont("vinerhanditc", 10)

basicFont16 = pygame.font.SysFont("Arial", 16)
basicFont14 = pygame.font.SysFont("Arial", 14)
basicFont12 = pygame.font.SysFont("Arial", 12)
basicFont10 = pygame.font.SysFont("Arial", 10)

"""
COLOURS
"""
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
DARK_BLUE = (0,0,125)
RED = (255,0,0)
GREEN = (0,190,0)
DARK_GREEN = (0, 125, 0)
MARSH_GREEN = (40, 90, 40)
LIGHT_GREEN = (0, 225, 0)
BROWN = (165,85,0)
LIGHT_BROWN = (200, 120, 0)
GREY = ( 50, 50, 50 )
LIGHT_GREY = ( 100, 100, 100 )
DARK_GREY = ( 30, 30, 30 )
PURPLE = (150,0,255)
LIGHT_BLUE = (0, 140, 240)
YELLOW = ( 150, 150, 0 )
ORANGE = ( 255, 140, 0 )

DEBUG = True
DEBUG_STRING = ""

controlColours = {
    "None": BLACK,
    "Marquisate": RED,
    "Eyrie": BLUE,
    "Woodland Alliance": GREEN,
    "Lizard Cult": DARK_GREEN,
    "Riverfolk": LIGHT_BLUE,
    "Grand Duchy": PURPLE,
    "Corvid Conspiracy": GREY,
    "Denizens": YELLOW,
    }

"""
IMAGES
"""

MARQUISATE_ICON_PATH = "Images/marquisateIcon.png"
EYRIE_ICON_PATH = "Images/eyrieIcon.png"
WOODLAND_ALLIANCE_ICON_PATH = "Images/woodlandAllianceIcon.png"
LIZARD_CULT_ICON_PATH = "Images/lizardCultIcon.png"
RIVERFOLK_ICON_PATH = "Images/riverfolkIcon.png"
DUCHY_ICON_PATH = "Images/duchyIcon.png"
CORVIDS_ICON_PATH = "Images/corvidsIcon.png"

"""
HELPER FUNCTIONS
"""
def rollDie( sides, rolls ):
    x = 0
    for i in range(rolls):
        x += random.randint(1,sides)
    return x

def debug_print( string ):
    if ( DEBUG ):
        global DEBUG_STRING
        DEBUG_STRING += string + "\n"

def debug_dump():
    if ( DEBUG ):
        global DEBUG_STRING
        print(DEBUG_STRING)
        DEBUG_STRING = ""

def debug_clear():
    if ( DEBUG ):
        global DEBUG_STRING
        DEBUG_STRING = ""

def distSq( pos1, pos2 ):
    return np.sum( np.square( pos1 - pos2 ) )

def drawText( screen, pos, string, font, colour ):
    text = font.render( string, True, colour )
    screen.blit( text, pos )

def outlineText( screen, pos, string, font, colour, bgColour ):
    offset = 1
    offsetPositions = np.array([[-offset, -offset], [offset, -offset], [-offset, offset], [offset, offset]])

    for offsetPosition in offsetPositions:
        drawText( screen, pos + offsetPosition, string, font, bgColour )

    drawText( screen, pos, string, font, colour )

def drawTextTable( screen, pos, texts, fonts, colours, spacing, backgroundColour, borderColour ):
    # Calculate the max width and height
    width = 0
    height = 0
    for i in range( len( texts ) ):
        text = texts[i]
        font = fonts[i]

        size = font.size( text )
        width = max( width, size[0] )
        height += size[1] + spacing

    # Add spacing to the top and sides
    height += spacing
    width += 2 * spacing
        
    # Draw the bounding box and all of the info
    if backgroundColour:
        pygame.draw.rect( screen, backgroundColour, [ pos[0], pos[1], width, height ] )
    if borderColour:
        pygame.draw.rect( screen, borderColour, [ pos[0], pos[1], width, height ], 1 )

    currWidth = spacing
    currHeight = spacing
    for i in range( len( texts ) ):
        text = texts[i]
        font = fonts[i]
        colour = colours[i]

        size = font.size( text )
        drawText( screen, [ pos[0] + currWidth, pos[1] + currHeight ], text, font, colour )

        currHeight += size[1] + spacing

    return ( width, height )

# Draw everywhere but this rectangle
def drawAntiRect( screen, rect, colour ):
    screenWidth = screen.get_width()
    screenHeight = screen.get_height()

    bgRects = [ [ 0, 0, rect[0], screenHeight ],
                [ rect[0] + rect[2], 0, screenWidth - rect[0] - rect[2], screenHeight ],
                [ 0, 0, screenWidth, rect[1] ],
                [ 0, rect[1] + rect[3], screenWidth, screenHeight - rect[1] - rect[3] ] ]

    for rect in bgRects:
        pygame.draw.rect( screen, colour, rect )

# Scale the image to match the size and return the scaled copy
# We will scale the larger side of the image to the size to keep it within the confines of whatever it's being drawn in
def getScaledImage( imagePath, size ):
    image = pygame.image.load( imagePath )
    imageSize = image.get_size()

    newSize = [ 0, 0 ]
    if imageSize[0] > imageSize[1]:
        newSize[0] = size
        newSize[1] = int( size * float( imageSize[1] ) / imageSize[0] )
    else:
        newSize[0] = int( size * float( imageSize[0] ) / imageSize[1] )
        newSize[1] = size

    image = pygame.transform.scale( image, newSize )
    return image
    
    
