# Imports for DB
import sqlite3

# Connection 
# conn = sqlite3.connect('recipes.db')
conn = sqlite3.connect('db_flavour_molecules.db')
c = conn.cursor()

# SQL Commands
# c.execute("""CREATE TABLE ar_recipes (
#     id int,
#     url text,
#     name text,
#     servings text,
#     author text,
#     time_required text,
#     energy real, 
#     fat real, 
#     carbohydrates real, 
#     protein real, 
#     fibre real, 
#     sodium real, 
#     num_ingredients int
# )""")

# c.execute("""CREATE TABLE ar_ratings (
#     recipe_id int, 
#     user_id int, 
#     rating int, 
#     site_rating real, 
#     date text    
# )""")

# c.execute("""CREATE TABLE ar_users (
#     id int, 
#     ar_id int, 
#     username text, 
#     home_city text, 
#     current_city text, 
#     join_date text, 
#     skill_level text, 
#     cooking_interests text, 
#     hobbies text   
# )""")

# c.execute("""CREATE TABLE ar_ingredients (
#     id int, 
#     recipe_id int, 
#     url text, 
#     ingredient text, 
#     amount text   
# )""")

# c.execute("""CREATE TABLE m_ingredients_with_ghge (
#     url text,
#     recipe text, 
#     ingredient text,
#     match text,
#     foodex2 text,
#     ghge_per_100g real,
#     lu_per_100g real,
#     weight real
# )""")




# c.execute('SELECT * FROM q_ingr_info;')
# print(c.fetchall())

# conn.commit()
# conn.close()

print('Hey from Python!')