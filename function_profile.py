# Imports for DB and CSV
import sqlite3
import csv

# DB Connection 
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# Function to Check if Ingredient Belongs to a List of Categories
def checkCat(ing_ID, checklist):
    query_Check_Cat = '''SELECT Ingredients_Profiles.category FROM Ingredients_Profiles WHERE Ingredients_Profiles.ing_ID = '{}';'''.format(ing_ID)
    c.execute(query_Check_Cat)
    category = c.fetchone()[0]
    if category in checklist: 
        return True
    else: 
        return False

# Function to calculate similarity between two ingredients based on flavour profile
def calculateSimilarity(Sweetness1:float, Sweetness2:float, Saltiness1:float, Saltiness2:float, Sourness1:float, Sourness2:float, Bitterness1:float, Bitterness2:float, Umami1:float, Umami2:float, Fat1:float, Fat2:float) -> float:
    diff_Sweetness = abs(Sweetness1 - Sweetness2)
    diff_Saltiness = abs(Saltiness1 - Saltiness2)
    diff_Sourness = abs(Sourness1 - Sourness2)
    diff_Bitterness = abs(Bitterness1 - Bitterness2)
    diff_Umami = abs(Umami1 - Umami2)
    diff_Fat = abs(Fat1 - Fat2)

    difference = (diff_Sweetness + diff_Saltiness + diff_Sourness + diff_Bitterness + diff_Umami + diff_Fat)/6
    return (10 - difference) # This will return difference score, subtracted from 10 (maximum possible value) can be used for similarity

# Main Function
def mainFunction(ingredient_ID, foodEx2Code, threshold_GHG, threshold_Similarity, threshold_Cat, g_factor, f_factor):
    
    # Queries to be executed:
    # GHG emissions of selected entry
    query_GHG = '''SELECT GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}';'''.format(foodEx2Code)
    c.execute(query_GHG)
    initial_GHG = float(c.fetchone()[0])

    # Flavour Profile of selected entry
    query_FP = '''SELECT Sweetness, Saltiness, Sourness, Bitterness, Umami, Fat FROM Ingredients_Profiles WHERE Ingredients_Profiles.ing_ID = '{}';'''.format(ingredient_ID)       
    c.execute(query_FP)
    initial_FP = c.fetchall()

    # Food Category of selected entry
    query_Cat = '''SELECT Ingredients_Profiles.category FROM Ingredients_Profiles WHERE Ingredients_Profiles.ing_ID = '{}';'''.format(ingredient_ID)
    c.execute(query_Cat)
    initial_Cat = c.fetchone()[0]

    # Get List of Ingredients with Same Category
    query_Similar_Ing = '''SELECT ing_ID FROM Ingredients_Profiles WHERE category = '{}' AND FoodEx2 != '-' AND FoodEx2 IS NOT NULL AND ing_ID != '{}';'''.format(initial_Cat, ingredient_ID)
    c.execute(query_Similar_Ing)
    similar_Ing = c.fetchall()

    # Get Attributes for each Similar Ingredient
    for index, ing in enumerate(similar_Ing):        
        # First Get GHG for each Ingredient
        query_Similar_Ing_GHG = '''SELECT SHARP_ID.GHGE_1kg_kgCO2eq FROM SHARP_ID INNER JOIN Ingredients_Profiles ON SHARP_ID.FoodEx2 = Ingredients_Profiles.FoodEx2 WHERE Ingredients_Profiles.ing_ID = '{}' LIMIT 1;'''.format(ing[0])    
        c.execute(query_Similar_Ing_GHG)
        similar_Ing_GHG = c.fetchone()
        similar_Ing[index]+=similar_Ing_GHG
        # Calculate % Change in GHG
        dec_GHG = ((initial_GHG - float(similar_Ing_GHG[0])) *100 / initial_GHG)     
        similar_Ing[index]+=(dec_GHG, )
        
        # Calculate Similarity Factor between initial and suggested factor (check calculateSimilarity() function)
        # First, get Flavour Profile of each ingredient
        query_Similar_Ing_FP = '''SELECT Sweetness, Saltiness, Sourness, Bitterness, Umami, Fat FROM Ingredients_Profiles WHERE Ingredients_Profiles.ing_ID = '{}';'''.format(ing[0])
        c.execute(query_Similar_Ing_FP)
        similar_Ing_FP = c.fetchall()       

        similarityScore = calculateSimilarity(float(initial_FP[0][0]), float(similar_Ing_FP[0][0]),
        float(initial_FP[0][1]),float(similar_Ing_FP[0][1]),
        float(initial_FP[0][2]),float(similar_Ing_FP[0][2]),
        float(initial_FP[0][3]),float(similar_Ing_FP[0][3]),
        float(initial_FP[0][4]),float(similar_Ing_FP[0][4]),
        float(initial_FP[0][5]),float(similar_Ing_FP[0][5]))

        similarityScore_Normalized = ((similarityScore/10)*100) #Transforms the score into percentage
        similar_Ing[index]+= (similarityScore_Normalized,)
        
        
        
    # Keep Ingredients with Positive GHG Change (i.e. less GHG emissions)
    similar_Ing[:] = [ing for ing in similar_Ing if ing[2] > 0]    

    # Function that calculates the rank for each similar molecule
    def ranking_function(ghg_difference, similarity):
        return (ghg_difference*g_factor+similarity*f_factor)

    # Create the Rank for Each of these Molecules and Filter Insignificant Data
    for index, ing in enumerate(similar_Ing):
        rank  = ranking_function(ing[2], ing[3])    
        similar_Ing[index]+=(rank, )
    
    # Filter out Undesired Ingredients
    # Remove Ingredients that don't pass the GHG reduction threshold
    similar_Ing[:] = [ing for ing in similar_Ing if ing[2] > threshold_GHG]
    # Remove Ingredients that don't pass the common FM threshold
    similar_Ing[:] = [ing for ing in similar_Ing if ing[3] > threshold_Similarity]
    # Remove Ingredients that belong to unwanted categories
    similar_Ing[:] = [ing for ing in similar_Ing if not checkCat(ing[0], threshold_Cat)]
    # Note: Can add more filters here 

    # Reorder list based on rank
    similar_Ing.sort(key=lambda similar_Ing: similar_Ing[4], reverse=True)

    # Return list of suggestions AS STRING to add to csv file
    suggestions_string = ''
    for index, ingredient in enumerate(similar_Ing): 
        query_Ing_Name = '''SELECT Ingredients_Profiles.Food FROM Ingredients_Profiles WHERE Ingredients_Profiles.ing_ID = '{}';'''.format(ingredient[0])
        c.execute(query_Ing_Name)
        ingredient_name = c.fetchone()    
        similar_Ing[index]+=ingredient_name
        suggestions_string += '@'+ingredient_name[0]    
    return suggestions_string or 'N/A'

# Create new CSV File and Add the Recommendations to it
def createFile_Profile(threshold_GHG, threshold_Similarity, threshold_Cat, g_factor, f_factor):
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
            ingredient_ID = row[9]
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
            'Swaps': row[14],
            'Swaps2': mainFunction(ingredient_ID, foodEx2Code, threshold_GHG, threshold_Similarity, threshold_Cat, g_factor, f_factor)})
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
            'Swaps': row[14],
            'Swaps2': 'NA'}) 
    in_file.close()    
    out_file.close()