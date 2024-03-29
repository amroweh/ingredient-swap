# Ingredient Swap 

*Disclaimer: the original version of this program was developed as part of a Master's dissertation submitted to the Information School at the University of Sheffield, Sheffield, UK.

## Introduction
This project contains the code files for the manipulation of the AllRecipes recipe and ingredient databases, along with their GHG emissions and Land Use Values.

Additionally, the project also has the flavour database from FlavourDB.

The purpose of this program is to attempt to link all these characteristics together in order to be able to swap ingredients with high GHG emissions with those of lower emissions.

## How the Code Works
All code files are in Python. The code contains three main files: main.py, functions_molecules.py, and functions_profile.py. You should run the main.py file. 

### Initial Parameters ###
The main.py file has a number of parameters that can be altered by the user:

**threshold_GHG:** 
Ingredients with GHG difference less than this threshold will not be considered. In other words, it would not be worth it to recommend this ingredient swap to the user because there is not significant GHG reductions associated with it. This is in percentage.

**threshold_FM:**
Ingredients with Common Flavour Molecules less than this threshold will not be considered. In other words, ingredients that have too few flavour molecules in common with the initial ingredient might be too different for the user and will therefore be discarded. This is in percentage.

**threshold_Cat:**
Ingredient categories in this list will be eliminated. Some ingredient categories can not be used to recommend an ingredient like the 'Dish' category. Other categories like seasonings are not feasible because they are used in very low quantities, hence their GHG emissions are not that significan, and their swap might affect taste significantly. 

**g_factor & f_factor:**
The g_factor and f_factor are used as coefficients for the GHG and Flavour matching respectively. Because these are the two main variables in our functions, one can assign different values to each in order to give more or less weight for the respective variable. 
These are numbers between 0 and 1, and must always add up to 1.

### Code Workings ###
Initially, the program checks the integrity of the variables that were given by the user. I.e., does the user abide by the constraints stated above. If not, the program terminates.

Second, the program runs the createFile() function. This function uses the csv library to do the following:
1. Reads a csv file called 'recipes' containing a list of recipes along with their ingredients, FoodEx2 code, ingredient ID..etc.
2. Using the FoodEx2 code and the Ingredient_ID, runs the mainFunction() function which creates a string of potential ingredient swaps. Depending on which createFile function, the program performs a specific main function. The two possibilities are either based on the flavour profile of a set of ingredients, or on the number of flavour molecules.
3. Creates a new csv file called 'newrecipes.csv'
4. Adds the suggested swaps generated by the mainFunction() to the last column called 'Swaps'

The mainFunction() function contains all the SQL statements that were performed in addition to any calculations that were necessary to order lists, filter values...etc. before generating the final list of potential swaps. This function is were the above parameters were used.

Notes: 
- The SQL statements used access a sqlite database that is not present on this github repository because it exceeds the file size allowance. The database is called 'recipes.db' and contains all required databases like AR, SHARP_ID, and FlavourDB.
- The 'recipes_backup.csv' file contains the same data as the 'recipes.csv' and is only present in case any unwanted changes occurr to the 'recipes.csv' file.

