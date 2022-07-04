# Imports for DB
import sqlite3

# Filter Variables
numIngredientSwaps = 5
minimumGHGReduction = 20
foodEx2Code = 'A0B9G'

# DB Connection 
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# Query Formulation For Possible Ingredient Swaps
query = '''SELECT Similar_Ingredient, Code, COUNT(*) AS Common_Flavour_Molecule_Number, GHGE, 
(GHGE - (SELECT SHARP_ID.GHGE_1kg_kgCO2eq FROM SHARP_ID WHERE SHARP_ID.FoodEx2 = '{}')) AS GHGE_Difference
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
LIMIT {};'''.format(foodEx2Code, foodEx2Code, foodEx2Code, foodEx2Code, numIngredientSwaps)

# Query Execution
suggestions = c.execute(query)
print(c.fetchall())

conn.commit()
conn.close()

print('\nQuery Performed Using Python!')