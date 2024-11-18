from WoodlandCommon import *
import pygame
import random

class Denizen:
    # Species that are likely to appear in a clearing based on the control
    controlSpecies = { "Marquisate" : ["Cat"],
                        "Eyrie" : ["Bird"],
                        "Woodland Alliance" : [],
                        "Lizard Cult" : ["Lizard", "Salamander"],
                        "Riverfolk" : ["Otter"],
                        "Grand Duchy" : ["Mole"],
                        "Corvid Conspiracy" : ["Crow", "Raven"],
                        "Denizens" : [],
                        "None" : []
                    }

    basicSpecies = ["Mouse", "Fox", "Rabbit"]
    commonSpecies = ["Sparrow", "Badger", "Beaver", "Hedgehog", "Mole", "Opossum", "Otter", "Duck", "Owl", "Raccoon", "Rat", "Skunk", "Squirrel", "Wolf"]
    uncommonSpecies = ["Cat", "Crow", "Raven", "Lizard", "Dog", "Ferret", "Stoat", "Hawk", "Weasel", "Bluejay"]
    rareSpecies = ["Bat", "Salamander", "Turtle", "Porcupine", "Frog", "Toad"]

    controlSpeciesWeight    = 0.5
    clearingSpeciesWeight   = 1.0
    basicSpeciesWeight      = 1.0
    commonSpeciesWeight     = 3.0
    uncommonSpeciesWeight   = 3.0
    rareSpeciesWeight       = 0.5

    speciesWeightSum = controlSpeciesWeight + clearingSpeciesWeight + basicSpeciesWeight + commonSpeciesWeight + uncommonSpeciesWeight + rareSpeciesWeight

    controlSpeciesFactor = controlSpeciesWeight / speciesWeightSum
    clearingSpeciesFactor = clearingSpeciesWeight / speciesWeightSum + controlSpeciesFactor
    basicSpeciesFactor = basicSpeciesWeight / speciesWeightSum + clearingSpeciesFactor
    commonSpeciesFactor = commonSpeciesWeight / speciesWeightSum + basicSpeciesFactor
    uncommonSpeciesFactor = uncommonSpeciesWeight / speciesWeightSum + commonSpeciesFactor
    rareSpeciesFactor = rareSpeciesWeight / speciesWeightSum + uncommonSpeciesFactor

    occupations = ["Mayor", "Smith", "Guard Captain", "Rebel Leader", "Enemy Captain", "Village Elder", "Farmer", "Thief", "Local Regent",
                   "Scholar", "Tax Collector", "Doctor", "Armorer", "Merchant", "Noble", "Astronomer", "Healer", "Banker",
                   "Rabble-Rouser", "Bandit", "Mercenary", "Baker", "Tracker", "Historian", "Recruiter", "Tailor", "Jeweler",
                   "Sheriff", "Barber", "Monk", "Soldier", "Mason", "Assassin", "Gambler", "Minstrel", "Judge"]

    names = ["Aimee", "Alvin", "Anders", "Alyse", "Bhea", "Billi", "Braden", "Buford", "Cesspyr", "Cinder", "Constance", "Cloak", "Dawna",
             "Dewly", "Doneel", "Dugan", "Ellaine", "Emmie", "Ewan", "Eward", "Flannera", "Fog", "Foster", "Frink", "Gemma", "Golden"
             "Greta", "Gustav", "Harper", "Henny", "Hinnic", "Howerd", "Igrin", "Ilso", "Inda", "Irwen", "Jacly", "Jasper", "Jinx",
             "Johann", "Keilee", "Keera", "Kagan", "Konnor", "Laina", "Lindyn", "Lockler", "Longtooth", "Masgood", "Mint", "Monca",
             "Murty", "Nail", "Nan", "Nigel", "Nomi", "Olaga", "Omin", "Orry", "Oxley", "Pattee", "Phona", "Pintin", "Prewitt", "Quay",
             "Quentin", "Quill", "Quinella", "Reece", "Rhodia", "Roric", "Rose", "Sarra", "Selwin", "Stasee", "Sorin", "Tammora", "Thickfur",
             "Timber", "Tondric", "Ulveny", "Ulvid", "Ummery", "Urma", "Vance", "Vennic", "Vittora", "Vost", "Wanda", "Wettlecress",
             "Whickam", "Woodleaf", "Xander", "Xara", "Xeelie", "Xim", "Yasmin", "Yates", "Yolenda", "Yotterie", "Zachrie", "Zain", "Zoic", "Zola"]
    

    def __init__( self ):
        self.occupation = ""
        self.species = ""
        self.name = random.choice( self.names )

    def generateSpecies( self, clearing ):
        rand = random.random()
        species = ""
        control = clearing.control
        clearingSpecies = clearing.residents

        # Make the species part of the controlling group of this clearing
        if rand < self.controlSpeciesFactor and ( control in self.controlSpecies ) and ( len( self.controlSpecies[control] ) > 0 ) :
            species = random.choice( self.controlSpecies[control] )
        elif rand < self.clearingSpeciesFactor:
            species = clearingSpecies
        elif rand < self.basicSpeciesFactor:
            species = random.choice( self.basicSpecies )
        elif rand < self.commonSpeciesFactor:
            species = random.choice( self.commonSpecies )
        elif rand < self.uncommonSpeciesFactor:
            species = random.choice( self.uncommonSpecies )
        elif rand < self.rareSpeciesFactor:
            species = random.choice( self.rareSpecies )

        self.species = species
    
