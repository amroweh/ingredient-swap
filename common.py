import sqlite3
import csv

from functions_molecules import mainFunction as main_Molecules
from functions_profile import mainFunction as main_Profile


# DB Connection 
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Function to Check the constraints Input by the User
def checkConstraints(threshold_GHG, threshold_FM, threshold_Cat, threshold_Similarity, g_factor, f_factor):    
    if (threshold_GHG < 0 or threshold_GHG > 100 
    or threshold_FM < 0 or threshold_FM > 100
    or g_factor < 0 or g_factor > 1
    or f_factor < 0 or f_factor > 1
    or g_factor+f_factor != 1
    or threshold_Similarity < 0 or threshold_Similarity > 100): return False
    

# Function to Check if Ingredient Belongs to a List of Categories
def checkCat(ing_ID, checklist, tableName, ingredientColumnName, categoryColumnName):
    query_Check_Cat = '''SELECT {} FROM {} WHERE {} = '{}';'''.format(categoryColumnName, tableName, ingredientColumnName, ing_ID)
    c.execute(query_Check_Cat)
    category = c.fetchone()[0]
    if category in checklist: 
        return True
    else: 
        return False

# Function to use mainFunctions output and write both to file
def createNewRecipes(threshold_GHG, threshold_FM, threshold_Similarity, threshold_Cat, g_factor, f_factor):
    print('Starting flavour profiles method...')
    in_file = open("recipes.csv")
    reader = csv.reader(in_file)
    out_file = open("newrecipes.csv", "w")
    fields = ('url','recipe','ingredient','match','foodex2','ghge_per_100g','lu_per_100g','weight','match_profile','match_profile_ID','Notes1','match_flavourDB','match_flavourDB_ID','Notes2','Swaps','Swaps2')
    writer = csv.DictWriter(out_file, fieldnames=fields, lineterminator = '\n')
    writer.writeheader()
    next(reader)
    for index, row in enumerate(reader):
        if index == 80:
            break
        try:        
            foodEx2Code = row[4]
            ingredient_ID_Molec = row[12]
            ingredient_ID_Prof = row[9]
            writer.writerow({'url': row[0],
            'recipe': row[1],
            'ingredient': row[2],
            'match': row[3],
            'foodex2': row[4],
            'ghge_per_100g': row[5],
            'lu_per_100g': row[6],
            'weight': row[7],
            'match_profile': row[8],
            'match_profile_ID': row[9],
            'Notes1': row[10],
            'match_flavourDB': row[11],
            'match_flavourDB_ID': row[12],
            'Notes2': row[13],
            'Swaps': main_Molecules(ingredient_ID_Molec, foodEx2Code, threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor),
            'Swaps2': main_Profile(ingredient_ID_Prof, foodEx2Code, threshold_GHG, threshold_Similarity, threshold_Cat, g_factor, f_factor)})
        except:
            writer.writerow({'url': row[0],
            'recipe': row[1],
            'ingredient': row[2],
            'match': row[3],
            'foodex2': row[4],
            'ghge_per_100g': row[5],
            'lu_per_100g': row[6],
            'weight': row[7],
            'match_profile': row[8],
            'match_profile_ID': row[9],
            'Notes1': row[10],
            'match_flavourDB': row[11],
            'match_flavourDB_ID': row[12],
            'Notes2': row[13],
            'Swaps': 'NA',
            'Swaps2': 'NA'}) 
    in_file.close()    
    out_file.close()