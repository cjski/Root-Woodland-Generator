import pygame
pygame.init()

from WoodlandCommon import *
from Woodland import *

import random
import math
import numpy as np
import pygame_widgets
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle


# Helper class to store the config data
class ConfigData:
    def __init__( self ):
        self.mapWidth = 1000
        self.mapHeight = 800
        self.numClearings = 12
        self.minClearingDist = 100

        self.forceLake = False
        self.forceRiver = False
        
        self.enableLake = True
        self.enableRiver = True
        
        self.enableMarquisate = True
        self.enableEyrie = True
        self.enableWoodlandAlliance = True
        self.enableLizardCult = True
        self.enableRiverfolk = True
        self.enableDuchy = True
        self.enableCorvids = True
        self.enableMountains = True
        self.enableMarshes = True
        self.enableLandmarks = True

    def getTextBoxAsInt( widget ):
        text = widget.getText()
        if text.isdigit():
            return int( text )
        else:
            return 0

    def setMapWidth( config, widget ):
        config.mapWidth = ConfigData.getTextBoxAsInt( widget )

    def setMapHeight( config, widget ):
        config.mapHeight = ConfigData.getTextBoxAsInt( widget )

    def setNumClearings( config, widget ):
        config.numClearings = ConfigData.getTextBoxAsInt( widget )

    def setMinClearingDist( config, widget ):
        config.minClearingDist = ConfigData.getTextBoxAsInt( widget )

    def setForceLake( config, widget ):
        config.forceLake = widget.getValue()

    def setForceRiver( config, widget ):
        config.forceRiver = widget.getValue()

    def setEnableLake( config, widget ):
        config.enableLake = widget.getValue()

    def setEnableRiver( config, widget ):
        config.enableRiver = widget.getValue()

    def setEnableMarquisate( config, widget ):
        config.enableMarquisate = widget.getValue()

    def setEnableEyrie( config, widget ):
        config.enableEyrie = widget.getValue()

    def setEnableWoodlandAlliance( config, widget ):
        config.enableWoodlandAlliance = widget.getValue()

    def setEnableLizardCult( config, widget ):
        config.enableLizardCult = widget.getValue()

    def setEnableRiverfolk( config, widget ):
        config.enableRiverfolk = widget.getValue()

    def setEnableDuchy( config, widget ):
        config.enableDuchy = widget.getValue()

    def setEnableCorvids( config, widget ):
        config.enableCorvids = widget.getValue()

    def setEnableMountains( config, widget ):
        config.enableMountains = widget.getValue()

    def setEnableMarshes( config, widget ):
        config.enableMarshes = widget.getValue()

    def setEnableLandmarks( config, widget ):
        config.enableLandmarks = widget.getValue()

# Global Data settings functions
def setUseClassicGraphics( config, widget ):
    GLOBAL_SETTINGS.useClassicGraphics = widget.getValue()
        
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


def updateSettingsMenu( screen, pos, spacing, configData, createWidgets ):
    maxWidth = 0
    widgets = []
    widgetCallbacks = []

    textBoxHeightBuffer = 10
    textBoxHalfHeightBuffer = textBoxHeightBuffer / 2
    toggleExtraSpacing = 10
    toggleHalfExtraSpacing = int( toggleExtraSpacing / 2 )
    
    # Draw the title
    titlePos = pos
    titleFont = font16
    titleText = "Woodland Settings"

    titleSize = titleFont.size( titleText )
    drawText( screen, titlePos, titleText, titleFont, BLACK )

    maxWidth = max( maxWidth, titleSize[0] )

    # Common toggles for the basic info
    commonPos = [ titlePos[0], titlePos[1] + titleSize[1] + spacing ]
    commonFont = font14
    commonText = "Common"

    commonTextSize = commonFont.size( commonText )
    drawText( screen, commonPos, commonText, commonFont, BLACK )

    maxWidth = max( maxWidth, commonTextSize[0] )

    commonVarsPos = [ commonPos[0], commonPos[1] + commonTextSize[1] + spacing ]
    commonVarsTexts = [ "Map Width", "Map Height", "Number of Clearings", "Minimum Space Between Clearings" ]
    commonVarsCallbacks = [ ConfigData.setMapWidth, ConfigData.setMapHeight, ConfigData.setNumClearings, ConfigData.setMinClearingDist ]
    commonVarsStartVals = [ str( configData.mapWidth ), str( configData.mapHeight ), str( configData.numClearings ), str( configData.minClearingDist ) ]
    commonVarsFont = basicFont14
    yOffset = 0

    for i in range( len( commonVarsTexts ) ):
        text = commonVarsTexts[i]
        textSize = commonVarsFont.size( text )
        textBoxX = commonVarsPos[0]
        textBoxY = commonVarsPos[1] + yOffset
        textBoxWidth = 60
        textBoxHeight = textSize[1] + textBoxHeightBuffer
        
        if createWidgets:
            textBox = TextBox( screen, textBoxX, textBoxY, textBoxWidth, textBoxHeight,
                               font=commonVarsFont, borderThickness=1 )
            textBox.setText( commonVarsStartVals[i] )
            widgets.append( textBox )
            widgetCallbacks.append( commonVarsCallbacks[i] )
        
        textPos = [ textBoxX + textBoxWidth + 2 * spacing, textBoxY + textBoxHalfHeightBuffer ]
        drawText( screen, textPos, text, commonVarsFont, BLACK )

        yOffset += spacing + textBoxHeight

        maxWidth = max( maxWidth, textSize[0] + textBoxWidth + spacing * 2 )

    # Faction on and off toggles
    factionsPos = [ commonVarsPos[0], commonVarsPos[1] + yOffset + spacing ]
    factionsFont = font14
    factionsText = "Factions Toggles"

    factionsTextSize = factionsFont.size( factionsText )
    drawText( screen, factionsPos, factionsText, factionsFont, BLACK )

    maxWidth = max( maxWidth, factionsTextSize[0] )

    factionNames = [ controlName for controlName in controlColours if controlName != "None" and controlName != "Denizens" ]
    factionCallbacks = {
        "Marquisate": ConfigData.setEnableMarquisate,
        "Eyrie": ConfigData.setEnableEyrie,
        "Woodland Alliance": ConfigData.setEnableWoodlandAlliance,
        "Lizard Cult": ConfigData.setEnableLizardCult,
        "Riverfolk": ConfigData.setEnableRiverfolk,
        "Grand Duchy": ConfigData.setEnableDuchy,
        "Corvid Conspiracy": ConfigData.setEnableCorvids,
        }
    factionStartVals = {
        "Marquisate": configData.enableMarquisate,
        "Eyrie": configData.enableEyrie,
        "Woodland Alliance": configData.enableWoodlandAlliance,
        "Lizard Cult": configData.enableLizardCult,
        "Riverfolk": configData.enableRiverfolk,
        "Grand Duchy": configData.enableDuchy,
        "Corvid Conspiracy": configData.enableCorvids,
        }
    factionVarsPos = [ factionsPos[0], factionsPos[1] + factionsTextSize[1] + spacing ]
    factionVarsFont = basicFont14
    yOffset = 0
    
    for i in range( len( factionNames ) ):
        text = factionNames[i]
        textSize = factionVarsFont.size( text )

        toggleX = factionVarsPos[0] + 2 * spacing
        toggleY = factionVarsPos[1] + yOffset + toggleHalfExtraSpacing
        toggleWidth = textSize[1]
        toggleHeight = textSize[1]

        if createWidgets:
            startOn = True
            if text in factionStartVals:
                startOn = factionStartVals[text]
            toggle = Toggle( screen, toggleX, toggleY, toggleWidth, toggleHeight, startOn=startOn )
            widgets.append( toggle )

            if text in factionCallbacks:
                widgetCallbacks.append( factionCallbacks[text] )
            else:
                widgetCallbacks.append( None )

        iconPos = [ toggleX + toggleWidth * 2 + spacing, toggleY ]
        iconSize = textSize[1] 
        drawFcn = Clearing.controlDict[ text ]
        
        if drawFcn != None:
            drawFcn( screen, iconPos, iconSize )
        
        textPos = [ iconPos[0] + iconSize + spacing, iconPos[1] ]
        drawText( screen, textPos, text, factionVarsFont, BLACK )

        yOffset += spacing + toggleHeight + toggleHalfExtraSpacing * 2

        maxWidth = max( maxWidth, textSize[0] + toggleWidth * 2 + iconSize + spacing * 5 )

    # Map Generation variables and toggles
    mapGenPos = [ factionVarsPos[0], factionVarsPos[1] + yOffset + spacing ]
    mapGenFont = font14
    mapGenText = "Map Generation Toggles"

    mapGenSize = mapGenFont.size( mapGenText )
    drawText( screen, mapGenPos, mapGenText, mapGenFont, BLACK )

    maxWidth = max( maxWidth, mapGenSize[0] )

    mapGenVarNames = [ "Enable Lake", "Force Lake Spawn", "Enable River", "Force River Spawn",
                       "Enable Mountains", "Enable Marshes", "Enable Landmarks" ]
    mapGenCallbacks = [ ConfigData.setEnableLake, ConfigData.setForceLake, ConfigData.setEnableRiver, ConfigData.setForceRiver,
                        ConfigData.setEnableMountains, ConfigData.setEnableMarshes, ConfigData.setEnableLandmarks ]
    mapGenVarStartValues = [ configData.enableLake, configData.forceLake, configData.enableRiver, configData.forceRiver,
                             configData.enableMountains, configData.enableMarshes, configData.enableLandmarks ]
    mapGenVarsPos = [ mapGenPos[0], mapGenPos[1] + mapGenSize[1] + spacing ]
    mapGenVarsFont = basicFont14
    yOffset = 0
    
    for i in range( len( mapGenVarNames ) ):
        text = mapGenVarNames[i]
        textSize = mapGenVarsFont.size( text )

        toggleX = mapGenVarsPos[0] + 2 * spacing
        toggleY = mapGenVarsPos[1] + yOffset + toggleHalfExtraSpacing
        toggleWidth = textSize[1]
        toggleHeight = textSize[1]

        if createWidgets:
            toggle = Toggle( screen, toggleX, toggleY, toggleWidth, toggleHeight, startOn=mapGenVarStartValues[i] )
            widgets.append( toggle )
            widgetCallbacks.append( mapGenCallbacks[i] )

        textPos = [ toggleX + toggleWidth * 2 + spacing, toggleY ]
        drawText( screen, textPos, text, mapGenVarsFont, BLACK )

        yOffset += spacing + toggleHeight + toggleHalfExtraSpacing * 2

        maxWidth = max( maxWidth, textSize[0] + toggleWidth * 2 + spacing * 4 )

    # Other Settings
    otherPos = [ mapGenVarsPos[0], mapGenVarsPos[1] + yOffset + spacing ]
    otherFont = font14
    otherText = "Other"

    otherSize = otherFont.size( otherText )
    drawText( screen, otherPos, otherText, otherFont, BLACK )

    maxWidth = max( maxWidth, otherSize[0] )

    otherVarNames = [ "Use Classic Graphics" ]
    otherCallbacks = [ setUseClassicGraphics ]
    otherVarStartValues = [ GLOBAL_SETTINGS.useClassicGraphics ]
    otherVarsPos = [ otherPos[0], otherPos[1] + otherSize[1] + spacing ]
    otherVarsFont = basicFont14
    yOffset = 0
    
    for i in range( len( otherVarNames ) ):
        text = otherVarNames[i]
        textSize = otherVarsFont.size( text )

        toggleX = otherVarsPos[0] + 2 * spacing
        toggleY = otherVarsPos[1] + yOffset + toggleHalfExtraSpacing
        toggleWidth = textSize[1]
        toggleHeight = textSize[1]

        if createWidgets:
            toggle = Toggle( screen, toggleX, toggleY, toggleWidth, toggleHeight, startOn=otherVarStartValues[i] )
            widgets.append( toggle )
            widgetCallbacks.append( otherCallbacks[i] )

        textPos = [ toggleX + toggleWidth * 2 + spacing, toggleY ]
        drawText( screen, textPos, text, otherVarsFont, BLACK )

        yOffset += spacing + toggleHeight + toggleHalfExtraSpacing * 2

        maxWidth = max( maxWidth, textSize[0] + toggleWidth * 2 + spacing * 4 )
    
    return ( [ maxWidth, otherVarsPos[1] + yOffset ], widgets, widgetCallbacks )

  
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
    minClearingDist = 100
    """
    ///////////////////////////////////
    """
    # Data for the mouse position checks
    localInfoDrawDist = 50.0
    localInfoDrawDistSq = localInfoDrawDist * localInfoDrawDist
    # Spacing between items
    spacing = 3
    buffer = 15
    # Buffer for the bottom and right edges of the map
    screen = pygame.display.set_mode( ( 1 ,1 ) )
    pygame.display.set_caption('Root Woodland')

    configData = ConfigData()
    
    # Do this once to figure out the size of the legend so we can place the map in the right spot
    legendSize = drawLegend( screen, (0, 0), spacing )

    mapPos = ( legendSize[0] + spacing, 0 )
    settingsMenuPos = ( mapPos[0] + mapSize[0] + spacing * 2, 0 )

    settingsMenuSize, widgets, widgetCallbacks = updateSettingsMenu( screen, settingsMenuPos, spacing, configData, True )
        
    screenSize = ( settingsMenuPos[0] + settingsMenuSize[0] + spacing, max( mapSize[1], legendSize[1], settingsMenuSize[1] ) + spacing + buffer )
    screen = pygame.display.set_mode( screenSize )
    
    woodland = Woodland( mapPos, mapSize, minClearingDist )
    woodland.generate( numClearings )
    
    running = True
    
    while running:
        # Main event updates
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    debug_clear()
                    
                    woodland = Woodland( mapPos, [ configData.mapWidth, configData.mapHeight ], configData.minClearingDist,
                                         configData.enableLake, configData.enableRiver, configData.forceLake, configData.forceRiver,
                                         configData.enableMarquisate, configData.enableEyrie, configData.enableWoodlandAlliance,
                                         configData.enableLizardCult, configData.enableRiverfolk, configData.enableDuchy,
                                         configData.enableCorvids, configData.enableMountains, configData.enableMarshes,
                                         configData.enableLandmarks )
                    woodland.generate( configData.numClearings )

                    settingsMenuPos = ( mapPos[0] + woodland.size[0] + spacing * 2, 0 )
                    settingsMenuSize, widgets, widgetCallbacks = updateSettingsMenu( screen, settingsMenuPos, spacing, configData, True )
        
                    screenSize = ( settingsMenuPos[0] + settingsMenuSize[0] + spacing, max( mapSize[1], legendSize[1], settingsMenuSize[1] ) + spacing + buffer )
                    screen = pygame.display.set_mode( screenSize )
                
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
        settingsMenuSize, _, _ = updateSettingsMenu( screen, settingsMenuPos, spacing, configData, False )

        # Update widgets
        pygame_widgets.update( events )
        for widgetIndex in range( len( widgets ) ):
            widgets[widgetIndex].draw()

            # Set our config data
            if widgetCallbacks[widgetIndex]:
                widgetCallbacks[widgetIndex]( configData, widgets[widgetIndex] )
        
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
