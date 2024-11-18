import pygame
pygame.init()
from WoodlandCommon import *
from Woodland import *

import random
import math
import numpy as np

"""
GAME
"""
def drawLegend( screen, pos, spacing ):
    # First draw the factions legend
    factionDrawPos = pos
    factionTexts = [ "Factions:" ]
    factionFonts = [ font16 ]
    factionColours = [ BLACK ]

    for controlName in controlColours:
        factionTexts.append( controlName )
        factionFonts.append( font12 )
        factionColours.append( controlColours[controlName] )

    factionDrawSize = drawTextTable( screen, factionDrawPos, factionTexts, factionFonts, factionColours, spacing, None, None )

    # Draw the features legend
    featureDrawPos = ( factionDrawPos[0], factionDrawPos[1] + factionDrawSize[1] + 2 * spacing )
    featureTexts = [ "Features:" ]
    featureFonts = [ font16 ]
    featureColours = [ BLACK ]

    for featureName in Clearing.featuresDict:
        data = Clearing.featuresDict[featureName]
        control = data[0]
        drawFcn = data[1]

        if drawFcn != None:
            featureTexts.append( featureName )
            featureFonts.append( font12 )
            featureColours.append( controlColours[control] )

    featureDrawSize = drawTextTable( screen, featureDrawPos, featureTexts, featureFonts, featureColours, spacing, None, None )

    # Draw the legend icons beside the faction and feature titles
    iconsDrawX = pos[0] + max( factionDrawSize[0], featureDrawSize[0] ) + spacing

    factionTitleSize = factionFonts[0].size( factionTexts[0] )
    # Offset the Y by the title and spacing to start drawing on the first faction line
    iconsDrawY = factionDrawPos[1] + factionTitleSize[1] + 2 * spacing

    iconsWidth = 0
    
    # Skip the first item because that's just the title
    for i in range( 1, len( factionTexts ) ):
        drawFcn = Clearing.controlDict[ factionTexts[i] ]
        size = factionFonts[i].size( factionTexts[i] )
        
        if drawFcn != None:
            iconPos = ( iconsDrawX, iconsDrawY )
            drawFcn( screen, iconPos, size[1] )
            iconsWidth = max( iconsWidth, size[1] )

        iconsDrawY += spacing + size[1]

    featureTitleSize = featureFonts[0].size( featureTexts[0] )
    # Offset the Y by the title and spacing to start drawing on the first faction line
    iconsDrawY = featureDrawPos[1] + featureTitleSize[1] + 2 * spacing

    # Skip the first item because that's just the title
    for i in range( 1, len( featureTexts ) ):
        drawFcn = Clearing.featuresDict[ featureTexts[i] ][1]
        size = featureFonts[i].size( featureTexts[i] )
        
        if drawFcn != None:
            iconPos = ( iconsDrawX, iconsDrawY )
            drawFcn( screen, iconPos, size[1] )
            iconsWidth = max( iconsWidth, size[1] )

        iconsDrawY += spacing + size[1]

    legendSize = ( iconsDrawX + iconsWidth, factionDrawSize[1] + 2 * spacing + featureDrawSize[1] )
    return legendSize
    
def main():
    """
    //////// EDITABLE VARIABLES ///////
    """
    # Size of the woodland map
    mapSize = ( 1000, 800 )
    # Number of clearings to spawn on the map
    numClearings = 12
    # Minimum distance between clearings. The map size needs to be big enough to handle the number of clearings
    # and the minimum distance between them or less clearings than set will spawn
    minClearingDist = 150
    """
    ///////////////////////////////////
    """
    # Data for the mouse position checks
    localInfoDrawDist = 50.0
    localInfoDrawDistSq = localInfoDrawDist * localInfoDrawDist
    # Spacing between items
    spacing = 3
    # Buffer for the bottom and right edges of the map
    buffer = 15
    screen = pygame.display.set_mode( ( 1 ,1 ) )
    pygame.display.set_caption('Root Woodland')
    
    # Do this once to figure out the size of the legend so we can place the map in the right spot
    legendSize = drawLegend( screen, (0, 0), spacing )

    mapPos = ( legendSize[0] + spacing, 0 )
    screenSize = ( mapPos[0] + mapSize[0] + spacing + buffer, max( mapSize[1], legendSize[1] ) + spacing + buffer )
    screen = pygame.display.set_mode( screenSize )
    
    woodland = Woodland( mapPos, mapSize, minClearingDist )
    woodland.generate( numClearings )
    
    woodland.draw( screen )
    drawAntiRect( screen, woodland.rect, WHITE )
    legendSize = drawLegend( screen, (0, 0), spacing )
    
    running = True
    pygame.display.update()
    
    while running:
        # Main event updates
        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    debug_clear()
                    woodland.generate( numClearings )
                elif event.key == pygame.K_d:
                    debug_dump()
                elif event.key == pygame.K_u:
                    woodland.update()
            
            if event.type == pygame.QUIT:
                running = False

        # Redraw the map, screen, and background
        woodland.draw( screen )
        drawAntiRect( screen, woodland.rect, WHITE )
        legendSize = drawLegend( screen, (0, 0), spacing )
        
        # If we're close enough to any clearings draw the local info
        mousePos = pygame.mouse.get_pos()
        
        closestClearing = None
        closestClearingDistSq = localInfoDrawDistSq
        for clearing in woodland.clearings:
            mouseToClearingDistSq = distSq( mousePos, clearing.pos )

            if mouseToClearingDistSq < localInfoDrawDistSq and mouseToClearingDistSq < closestClearingDistSq:
                closestClearing = clearing
                closestClearingDistSq = mouseToClearingDistSq
                
        if closestClearing:
            infoDrawPos = [ mousePos[0] + 10, mousePos[1] ]
            closestClearing.drawLocalInfo( screen, infoDrawPos )

        # Update display
        pygame.display.update()

    pygame.quit()

if __name__ == '__main__':
    main()
