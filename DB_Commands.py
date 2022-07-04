# Imports for DB
import sqlite3

# Filter Variables
numIngredientSwaps = 5
minimumGHGReduction = 20
foodEx2Code = 'A01SP'

# DB Connection 
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# Query Formulation For Possible Ingredient Swaps
query = '''SELECT DISTINCT Ingredients.entity_alias_readable AS Similar_Ingredients, 
Ingredients.FoodEx2 AS Code, 
Ingredients.category_readable AS Category, 
SHARP_ID.GHGE_1kg_kgCO2eq AS GHG FROM Ingredients
INNER JOIN SHARP_ID
ON Ingredients.FoodEx2 = SHARP_ID.FoodEx2
WHERE Similar_Ingredients IN (SELECT Ingredients.entity_alias_readable FROM Ingredients WHERE Ingredients.category_readable = (SELECT Ingredients.category_readable FROM Ingredients WHERE Ingredients.FoodEx2 = '{}'))
AND Code <> '{}'
ORDER BY GHG ASC
LIMIT {};'''.format(foodEx2Code, foodEx2Code, numIngredientSwaps)

# Query Execution
suggestions = c.execute(query)

print(query)
print(c.fetchall())

conn.commit()
conn.close()

print('Query Performed Using Python!')