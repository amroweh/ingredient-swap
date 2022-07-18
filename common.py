import sqlite3
import sys


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