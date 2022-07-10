# Imports for DB and CSV
import sqlite3
import csv

# DB Connection 
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# Function to Check if Ingredient Belongs to a List of Categories
def checkCat(ing_ID, checklist):
    query_Check_Cat = '''SELECT Ingredients.new_category FROM Ingredients WHERE Ingredients.entity_id = '{}';'''.format(ing_ID)
    c.execute(query_Check_Cat)
    category = c.fetchone()[0]
    if category in checklist: 
        return True
    else: 
        return False

# Main Function
def mainFunction(ingredient_ID, foodEx2Code, threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor):
    # Queries to be executed:
    # GHG emissions of selected entry
    query_GHG = '''SELECT GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}';'''.format(foodEx2Code)
    c.execute(query_GHG)
    initial_GHG = float(c.fetchone()[0])

    # Number of Flavour Molecules of selected entry
    query_FM = '''SELECT COUNT(Flavour_Molecules.compound_id) FROM Flavour_Molecules INNER JOIN Ingredients ON Ingredients.entity_id = Flavour_Molecules.ingredient_id WHERE Flavour_Molecules.ingredient_id = '{}';'''.format(ingredient_ID)
    c.execute(query_FM)
    initial_FM = float(c.fetchone()[0])

    # Food Category of selected entry
    query_Cat = '''SELECT Ingredients.new_category FROM Ingredients WHERE Ingredients.entity_id = '{}';'''.format(ingredient_ID)
    c.execute(query_Cat)
    initial_Cat = c.fetchone()[0]

    # Get List of Ingredients with Same Category
    query_Similar_Ing = '''SELECT entity_id FROM Ingredients WHERE new_category = '{}' AND FoodEx2 != '-' AND FoodEx2 IS NOT NULL AND entity_id != '{}';'''.format(initial_Cat, ingredient_ID)
    c.execute(query_Similar_Ing)
    similar_Ing = c.fetchall()

    # Get Attributes for each Similar Ingredient
    for index, ing in enumerate(similar_Ing):        
        # First Get GHG for each Ingredient
        query_Similar_Ing_GHG = '''SELECT SHARP_ID.GHGE_1kg_kgCO2eq FROM SHARP_ID INNER JOIN Ingredients ON SHARP_ID.FoodEx2 = Ingredients.FoodEx2 WHERE Ingredients.entity_id = '{}' LIMIT 1;'''.format(ing[0])    
        c.execute(query_Similar_Ing_GHG)
        similar_Ing_GHG = c.fetchone()
        similar_Ing[index]+=similar_Ing_GHG
        # Calculate % Change in GHG
        dec_GHG = ((initial_GHG - float(similar_Ing_GHG[0])) *100 / initial_GHG)     
        similar_Ing[index]+=(dec_GHG, )
        # Get Number of Common Flavour Molecules for each Similar Ingredient
        query_Similar_Ing_FM = '''SELECT COUNT(compound_id) FROM Flavour_Molecules WHERE ingredient_id = '{}' AND compound_id IN (SELECT compound_id FROM Flavour_Molecules WHERE ingredient_id = '{}');'''.format(ing[0], ingredient_ID)    
        c.execute(query_Similar_Ing_FM)
        similar_Ing_FM = c.fetchone()
        similar_Ing[index]+= ((similar_Ing_FM[0]*100/initial_FM), ) # Divided by initial FM number to get percentage
        
    # Keep Ingredients with Positive GHG Change (i.e. less GHG emissions)
    similar_Ing[:] = [ing for ing in similar_Ing if ing[2] > 0]

    # Function that calculates the rank for each similar molecule
    def ranking_function(ghg_difference, common_flavour_molecules):
        return (ghg_difference*g_factor+common_flavour_molecules*f_factor) 

    # Create the Rank for Each of these Molecules and Filter Insignificant Data
    for index, ing in enumerate(similar_Ing):
        rank  = ranking_function(ing[2], ing[3])    
        similar_Ing[index]+=(rank, )

    # Filter out Undesired Ingredients
    # Remove Ingredients that don't pass the GHG reduction threshold
    similar_Ing[:] = [ing for ing in similar_Ing if ing[2] > threshold_GHG]
    # Remove Ingredients that don't pass the common FM threshold
    similar_Ing[:] = [ing for ing in similar_Ing if ing[3] > threshold_FM]
    # Remove Ingredients that belong to unwanted categories
    similar_Ing[:] = [ing for ing in similar_Ing if not checkCat(ing[0], threshold_Cat)]
    # Note: Can add more filters here 

    # Reorder list based on rank
    similar_Ing.sort(key=lambda similar_Ing: similar_Ing[4], reverse=True)

    # Return list of suggestions AS STRING to add to csv file
    suggestions_string = ''
    for index, ingredient in enumerate(similar_Ing): 
        query_Ing_Name = '''SELECT Ingredients.entity_alias_readable FROM Ingredients WHERE Ingredients.entity_id = '{}';'''.format(ingredient[0])
        c.execute(query_Ing_Name)
        ingredient_name = c.fetchone()    
        similar_Ing[index]+=ingredient_name
        suggestions_string += '@'+ingredient_name[0]    
    return suggestions_string or 'N/A'
     
# Create new CSV File and Add the Recommendations to it
def createFile(threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor):
    in_file = open("recipes.csv")
    reader = csv.reader(in_file)
    out_file = open("newrecipes.csv", "w")
    fields = ('url','recipe','ingredient','match','foodex2','ghge_per_100g','lu_per_100g','weight','match_profile','match_profile_ID','Notes1','match_flavourDB','match_flavourDB_ID','Notes2','Swaps')
    writer = csv.DictWriter(out_file, fieldnames=fields, lineterminator = '\n')
    writer.writeheader()
    next(reader)
    for index, row in enumerate(reader):
        if index == 80:
            break
        try:        
            foodEx2Code = row[4]
            ingredient_ID = row[12]
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
            'Swaps': mainFunction(ingredient_ID, foodEx2Code, threshold_GHG, threshold_FM, threshold_Cat, g_factor, f_factor)})
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
            'Swaps': 'NA'}) 
    in_file.close()    
    out_file.close()