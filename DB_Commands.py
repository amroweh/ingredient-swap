# Imports for DB and CSV
import sqlite3
import pandas as pd

# Main Function 
def mainFunction(ingredient_ID, foodEx2Code):
    # Filter Variables
    numIngredientSwaps = 5
    minimumGHGReduction = 20
    # Ingredient ID and FoodEx2 Must Match and are in the Test CSV File
    # ingredient_ID = '271'
    # foodEx2Code = 'A0B9G'
    maxGHG = 74.88941836
    minGHG = 0
    rangeGHG = maxGHG - minGHG

    # To Set Importance of GHG vs. Flavour_Molecules
    g_factor = 0.2;
    f_factor = 0.8;

    # DB Connection 
    conn = sqlite3.connect('db_flavour_molecules.db')
    c = conn.cursor()

    # Initial query to determine GHG emissions and number of flavour molecules of selected entry
    initial_query_GHG = '''SELECT GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}' '''.format(foodEx2Code)
    c.execute(initial_query_GHG)
    initial_ghg = float(c.fetchone()[0])

    initial_query_FM = '''SELECT COUNT(Flavour_Molecules.compound_id) FROM Flavour_Molecules INNER JOIN Ingredients ON Ingredients.entity_id = Flavour_Molecules.ingredient_id WHERE Flavour_Molecules.ingredient_id = '{}';'''.format(ingredient_ID)
    c.execute(initial_query_FM)
    initial_FM = float(c.fetchone()[0])


    # Query Formulation For Ingredient Swaps
    query = '''SELECT Similar_Ingredient, Code, (COUNT(*)*100.0/(SELECT COUNT(Flavour_Molecules.compound_id) FROM Flavour_Molecules INNER JOIN Ingredients ON Ingredients.entity_id = Flavour_Molecules.ingredient_id WHERE Flavour_Molecules.ingredient_id = '{}'))  AS Common_Flavour_Molecule_Number, GHGE, 
    ((GHGE - (SELECT SHARP_ID.GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}'))*100/(SELECT SHARP_ID.GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}')) AS GHGE_Difference,
    GHGE AS Rank /* This is only to be used later to create the rank, it doesn't have any meaning yet */
    FROM (SELECT Flavour_Molecules.compound_id AS Flavour_ID, Flavour_Molecules.compound_name AS Flavour_Molecule, Ingredients.FoodEx2 as Code, Ingredients.entity_alias_readable AS Similar_Ingredient, SHARP_ID.GHGE_1kg_kgCO2eq AS GHGE FROM Flavour_Molecules 
    INNER JOIN Ingredients, SHARP_ID
    ON Ingredients.entity_id = Flavour_Molecules.ingredient_id
    AND Ingredients.FoodEx2 = SHARP_ID.FoodEx2
    WHERE Code IN (SELECT DISTINCT Ingredients.FoodEx2 AS Code FROM Ingredients INNER JOIN SHARP_ID ON Ingredients.FoodEx2 = SHARP_ID.FoodEx2
    /* Select ingredients with same category as selected ingredient */
    WHERE Ingredients.entity_alias_readable IN (SELECT Ingredients.entity_alias_readable FROM Ingredients WHERE Ingredients.category_readable = (SELECT Ingredients.category_readable FROM Ingredients WHERE Ingredients.FoodEx2 = '{}'))
    AND Code <> '{}'
    GROUP BY Code
    ORDER BY SHARP_ID.GHGE_1kg_kgCO2eq ASC)
    /* Select Ingredients that have common flavour molecules with the selected ingredient */
    AND Flavour_ID IN (SELECT Flavour_Molecules.compound_id AS Flavour_IDs FROM Flavour_Molecules 
    INNER JOIN Ingredients
    ON Ingredients.entity_id = Flavour_Molecules.ingredient_id
    WHERE Ingredients.FoodEx2 = '{}'))
    /* List Items that have lower GHG Emissions only */
    WHERE GHGE_Difference < 0
    GROUP BY Code
    /* Items that have more in common flavour molecues are higher */
    ORDER BY Common_Flavour_Molecule_Number DESC
    /* Limit number of possible ingredient swap */
    LIMIT {};'''.format(ingredient_ID, foodEx2Code, foodEx2Code, foodEx2Code, foodEx2Code, foodEx2Code, numIngredientSwaps)

    # Query Execution
    c.execute(query)
    suggestions = c.fetchall()
    print('Suggestions:\n')
    print(suggestions)

    # Query manipulation
    # Copy list into new list
    suggestions_with_rank = suggestions.copy()
    # Convert list of tuples to list of lists to allow modification
    suggestions_with_rank = [list(elem) for elem in suggestions_with_rank]

    # Function to determine the rank of each suggested molecule
    def ranking_function(ghg_difference, common_flavour_molecules):
        # The SQL query returns 
        return (-ghg_difference*g_factor+common_flavour_molecules*f_factor)        

    # Modify last column to hold final rank value
    for index, ingredient in enumerate(suggestions_with_rank): 
        ghg_difference = ingredient[4]
        common_flavour_molecules = ingredient[2]    
        ingredient[5] = ranking_function(ghg_difference, common_flavour_molecules)

    # Re-order list based on rank
    suggestions_with_rank.sort(key=lambda suggestions_with_rank: suggestions_with_rank[5], reverse=True)

    # Print final result
    print('\nRanked Suggestions:\n')
    print(suggestions_with_rank)

    # Close connection to DB
    conn.commit()
    conn.close()

    # Return list of suggestions
    return suggestions_with_rank

# Access File
recipes = pd.read_csv('recipes.csv', index_col=0)
for index, row in recipes.iloc[0:5].iterrows():    
    foodEx2Code = recipes['foodex2']
    ingredient_ID = recipes['match_flavourDB_ID']
    recipes['Swaps'] = mainFunction(ingredient_ID, foodEx2Code)

for index, row in recipes.iloc[0:5].iterrows():        
    print(row['Swaps'])


# Add Results to New File
#recipes.to_excel('newfile.xlsx', sheet_name='Ingredient Suggestions', index=False)

print('\nEnd of Program...')