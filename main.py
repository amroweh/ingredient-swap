from functions import createFile
from functions import checkConstraints

# Preset Conditions
threshold_GHG = 5 # Ingredients with GHG difference less than this threshold (%) will not be considered
threshold_FM = 10 # Ingredients with Common Flavour Molecules less than this threshold (%) will not be considered
threshold_Cat = ('Dish', 'Other', 'Bakery', 'Additive') # Ingredient categories in this list will be eliminated

# To Set Importance of GHG vs. Flavour_Molecules (Sum must equal 1)
g_factor = 0.2
f_factor = 0.8

print('Start of Function...\nWorking On It...')

# Checks constraints
if checkConstraints(threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor) == False: exit()

# Creates a modified csv file called 'newrecipes.csv' containing suggestions or 'N/A' if not possible
createFile(threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor)

print('End of Function...')