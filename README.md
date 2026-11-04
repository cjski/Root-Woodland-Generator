# Root-Woodland-Generator

<img width="2055" height="1327" alt="image" src="https://github.com/user-attachments/assets/b2642f91-54eb-4d37-b798-8bebdc092812" />

This is a generator for quickly creating random Woodland maps for the Root RPG. The majority of the logic is taken straight from the Root RPG Core Books with a few tweaks to make the maps look good and more connected.

## Recently added features
- Save and Load
- UI for generation instead of keyboard presses
- Hundreds and Keepers in Iron
- Update log
- Improved update logic (Factions won't try to do something they currently can't)
- Editable clearings

## Features
- All the currently supported factions in the RPG
- Denizen/Building/Problem generation
- River/Lake generation
- Clearing name generation based on local features like the river, marsh, mountains, lake, etc.
- Faction wartime updates from the Travelers and Outsiders book
- Landmark generation for interesting locations outside of the clearings
- Clearing war status system
- Customization options
- Map decoration drawing systems
- Editable Clearings

## Necessary Modules
- python
- pygame
- numpy
- scipy
- pygame_widgets
  
## How to use
- Install python and the modules listed above
- Download the repository or copy the files to your local folder
- Run the `GenerateWoodland.py` file in your IDE or through command line with `python GenerateWoodland.py`
- Hit the `Regen` button to generate a new map
- Hit the `Update` button to do an update of the Woodland war (As outlined in the Travelers and Outsiders book)
  - This will cause the factions to build, attack, fortify, spread or do any other specific actions unique to their faction

![image](https://github.com/user-attachments/assets/166b30a4-96c1-4f32-b542-cded9541d79c)
- Hover over a clearing to see extra information associated with it, like war status and local denizens

![image](https://github.com/user-attachments/assets/850d7a29-90a4-4561-8990-f067ea79a8a6)

## Editing Clearings
- Click on a Clearing to show the edit menu and all options for modifying the clearing

<img width="2053" height="1216" alt="image" src="https://github.com/user-attachments/assets/6e5d13e6-e7f3-48a5-a58f-41e7e8841295" />

## Customizing the Woodland
- The basic customization options are now in the UI for easier access and faster iteration of different maps, you can edit the size, number of clearings, and enabled features and factions
  - Note that the minimum number of Clearings will always be 4, below that the control doesn't work as well and maps don't look good
  - The minimum map size is also 500 by 500 units, below that and it's too small to really see anything

![image](https://github.com/user-attachments/assets/8e364df4-ccc4-4069-bce9-bb541fdb0e3a)
![image](https://github.com/user-attachments/assets/a72263d3-b449-4480-b97b-25209b1aea37)

- Outside of those, there are a ton of variables inside the files themselves that you can tweak to make things look the way you want to

![image](https://github.com/user-attachments/assets/8509f266-651b-4230-b4d2-51effeeba4d0)

## References
- Images of the Root Factions are from the Root Board Game and Kyle Ferrin

