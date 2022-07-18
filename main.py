from functions_molecules import createFile_Molecules
from functions_molecules import checkConstraints
from functions_profile import createFile_Profile
from test import createFile_ID
import sys 

# Preset Conditions
# For Flavour Molecules Method:
threshold_GHG = 5 # Ingredients with GHG difference less than this threshold (%) will not be considered
threshold_FM = 10 # Ingredients with Common Flavour Molecules less than this threshold (%) will not be considered
threshold_Cat = ('Dish', 'Other', 'Bakery', 'Additive') # Ingredient categories in this list will be eliminated
# For Flavour Profile Method:
threshold_Similarity = 60 # Ingredients with flavour similarity score less than this threshold (%) will not be considered

# To Set Importance of GHG vs. Flavour_Molecules (Sum must equal 1)
g_factor = 0.2
f_factor = 0.8

print('Start of Function...\nWorking On It...')

if checkConstraints(threshold_GHG, threshold_FM, threshold_Cat, threshold_Similarity, g_factor, f_factor) == False: sys.exit('You have an error in the parameters. Please check the conditions of these parameters and try again...')

# Creates a modified csv file called 'newrecipes.csv' containing suggestions or 'N/A' if not possible
#createFile_Molecules(threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor)
createFile_Profile(threshold_GHG, threshold_Similarity, threshold_Cat, g_factor, f_factor)
#createFile_ID()

print('End of Function...')