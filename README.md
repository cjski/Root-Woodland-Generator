# Root-Woodland-Generator

![image](https://github.com/user-attachments/assets/6b665a93-20a2-4c5a-84fc-c7f4597bda87)

This is a generator for quickly creating random Woodland maps for the Root RPG. The majority of the logic is taken straight from the Root Core Book and Travelers and Outsiders (For the additional factions) with a few tweaks to make the maps look good and more connected. 

## Features
- All the currently supported factions in the RPG
- Denizen/Building/Problem generation
- River/Lake generation
- Clearing name generation based on local features like the river, marsh, mountains, lake, etc.
- Faction wartime updates from the Travelers and Outsiders book
- Landmark generation for interesting locations outside of the clearings
- Clearing war status system

## Necessary Modules
- python
- pygame
- numpy
- scipy
  
## How to use
- Install python and the modules listed above
- Download the repository or copy the files to your local folder
- Run the `GenerateWoodland.py` file in your IDE or through command line with `python GenerateWoodland.py`

![image](https://github.com/user-attachments/assets/2215705b-108b-4e62-b944-da36e4edfd44)
- Hit the `R` key to generate a new map
- Hit the `U` key to do an update of the Woodland war (As outlined in the Travelers and Outsiders book)
  - This will cause the factions to build, attack, fortify, spread or do any other specific actions unique to their faction

![image](https://github.com/user-attachments/assets/166b30a4-96c1-4f32-b542-cded9541d79c)
- Hover over a clearing to see extra information associated with it, like war status and local denizens

![image](https://github.com/user-attachments/assets/850d7a29-90a4-4561-8990-f067ea79a8a6)


## Customizing the Woodland
- The basic customization options can be found in `GenerateWoodland.py`, just do a search for `EDITABLE VARIABLES`
  - `mapSize`, `numClearings`, and `minClearingDist` will let you create more dense or sparse maps
  - Note that the minimum number of Clearings will always be 4, below that the control doesn't work as well and maps don't look good

![image](https://github.com/user-attachments/assets/8e364df4-ccc4-4069-bce9-bb541fdb0e3a)
![image](https://github.com/user-attachments/assets/a72263d3-b449-4480-b97b-25209b1aea37)

- Outside of those, there are a ton of variables in the other files that you can tweak to make things look the way you want to

![image](https://github.com/user-attachments/assets/cf34c4d5-7c27-4042-96be-6b2b0e5a02c0)

