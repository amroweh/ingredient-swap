# Imports for DB
import sqlite3

# Connection 
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# Query Formulation
# Query to link Ingredients from Flavour Molecules DB to SHARP-ID
c.execute('''SELECT Ingredients.entity_alias_readable AS Ingredient, 
SHARP_ID.GHGE_1kg_kgCO2eq AS GHG, 
SHARP_ID."LU_1kg_m2/yr" AS LU
FROM Ingredients 
INNER JOIN SHARP_ID
ON Ingredients.FoodEx2 = SHARP_ID.FoodEx2
WHERE Ingredients.FoodEx2 = 'A036V';''')

print(c.fetchall())

conn.commit()
conn.close()

print('Query Performed Using Python!')