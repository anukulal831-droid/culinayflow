from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector # Changed from sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret_chef_key"

db_config = {
    'host': '127.0.0.1', 
    'user': 'root',
    'password': '', 
    'port': 3306,      
    'database': 'delfood_db'
}
def init_db():
    try:
        # Connect without database first to ensure it exists
        conn = mysql.connector.connect(host='localhost', user='root', password='')
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS delfood_db")
        cursor.execute("USE delfood_db")
        
        # Create the users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("WAMP MySQL Database & Table Ready!")
    except Exception as e:
        print(f"Error connecting to WAMP: {e}")

init_db()

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
        conn.commit()
        
        # 🚨 LOG THEM IN AUTOMATICALLY AFTER SIGNUP
        session['user_name'] = email 
        
        cursor.close()
        conn.close()
        return redirect(url_for('home'))
    except Exception as e:
        return f"Error: {e}"

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        # 🚨 STORE NAME IN SESSION
        session['user_name'] = email 
        return redirect(url_for('home'))
    else:
        return "Invalid credentials!"

@app.route('/logout')
def logout():
    # 🚨 CLEAR THE SESSION
    session.pop('user_name', None)
    return redirect(url_for('home'))

@app.route('/generate-recipe', methods=['POST'])
def generate_recipe():
    if 'user_name' not in session:
        return """
        <script>
            alert('Please login first to generate food.');
            window.location.href = '/';
        </script>
        """

    ingredients_input = request.form.get('ingredients', '').strip()
    meal_type = request.form.get('meal_type', 'lunch').strip().lower()
    utensils = request.form.getlist('utensils')
    time_available = request.form.get('time_available', '30').strip()
    skill_level = request.form.get('skill_level', 'beginner').strip().lower()
    chef_mode = request.form.get('chef_mode', 'gourmet').strip().lower()
    diet = request.form.get('diet', 'balanced').strip().lower()
    goal = request.form.get('goal', 'maintain').strip().lower()

    if not ingredients_input:
        ingredients_input = "rice, vegetables, onion"

    ingredients = [i.strip().lower() for i in ingredients_input.split(',') if i.strip()]
    display_ingredients = ", ".join([i.title() for i in ingredients])

    def has(item):
        return item in ingredients

    def has_any(items):
        return any(item in ingredients for item in items)

    def utensil_available(name):
        return name.lower() in [u.lower() for u in utensils]

    time_available = int(time_available) if str(time_available).isdigit() else 30

    selected_ingredients = ingredients.copy()
    unused_ingredients = []

    if chef_mode == "gourmet":
        if has("chicken") and has("rice"):
            selected_ingredients = [i for i in ingredients if i in ["chicken", "rice", "onion", "tomato", "garlic", "ginger", "curd", "yogurt", "coriander", "mint", "lemon"]]
        elif has("pasta"):
            selected_ingredients = [i for i in ingredients if i in ["pasta", "tomato", "cheese", "garlic", "onion", "milk", "cream", "butter", "capsicum", "oregano"]]
        elif has("paneer"):
            selected_ingredients = [i for i in ingredients if i in ["paneer", "onion", "tomato", "garlic", "ginger", "cream", "butter", "capsicum", "coriander"]]
        elif has_any(["egg", "eggs"]):
            selected_ingredients = [i for i in ingredients if i in ["egg", "eggs", "bread", "onion", "tomato", "cheese", "milk", "pepper", "butter"]]
        else:
            selected_ingredients = ingredients[:5]

        unused_ingredients = [i for i in ingredients if i not in selected_ingredients]

    selected_display = ", ".join([i.title() for i in selected_ingredients])
    unused_display = ", ".join([i.title() for i in unused_ingredients]) if unused_ingredients else "None"

    recipe_title = "Smart Pantry Recipe"
    cuisine = "TasteAtlas Style"
    recipe_steps = []

    if has("chicken") and has("rice"):
        recipe_title = "One-Pot Chicken Rice"
        if time_available <= 20:
            recipe_steps = [
                {
                    "time": "0:00 Min",
                    "title": "Quick Prep",
                    "description": "Wash rice and cut chicken into small pieces so it cooks faster. Slice onion and tomato thinly.",
                    "icon": "fa-solid fa-utensils"
                },
                {
                    "time": "5:00 Min",
                    "title": "Fast Masala Base",
                    "description": "Heat oil on the stove. Add onion, tomato, ginger-garlic paste, turmeric, chilli powder, and salt. Cook until soft.",
                    "icon": "fa-solid fa-fire"
                },
                {
                    "time": "10:00 Min",
                    "title": "Cook Chicken and Rice",
                    "description": "Add chicken pieces and rice. Add hot water, cover, and cook until rice is soft and chicken is cooked.",
                    "icon": "fa-solid fa-pot-food"
                },
                {
                    "time": "20:00 Min",
                    "title": "Serve",
                    "description": "Mix gently and serve hot with curd, salad, or lemon.",
                    "icon": "fa-solid fa-plate-wheat"
                }
            ]
        else:
            recipe_steps = [
                {
                    "time": "0:00 Min",
                    "title": "Marinate Chicken",
                    "description": "Mix chicken with salt, turmeric, chilli powder, ginger-garlic paste, lemon juice, and curd if available. Rest for 10 minutes.",
                    "icon": "fa-solid fa-bowl-food"
                },
                {
                    "time": "10:00 Min",
                    "title": "Prepare Rice",
                    "description": "Wash rice 2 to 3 times and soak it while preparing the masala.",
                    "icon": "fa-solid fa-bowl-rice"
                },
                {
                    "time": "20:00 Min",
                    "title": "Cook Masala",
                    "description": "Heat oil in a deep pan. Add onion and cook until golden. Add tomato and spices. Cook until the masala becomes thick.",
                    "icon": "fa-solid fa-fire"
                },
                {
                    "time": "30:00 Min",
                    "title": "Cook Chicken",
                    "description": "Add marinated chicken and cook until it absorbs the masala and becomes half cooked.",
                    "icon": "fa-solid fa-drumstick-bite"
                },
                {
                    "time": "40:00 Min",
                    "title": "Add Rice",
                    "description": "Add soaked rice and water. Cover and cook on low flame until rice and chicken are fully cooked.",
                    "icon": "fa-solid fa-pot-food"
                },
                {
                    "time": "50:00 Min",
                    "title": "Serve",
                    "description": "Garnish with coriander or mint. Serve hot with salad or raita.",
                    "icon": "fa-solid fa-plate-wheat"
                }
            ]

    elif has("pasta"):
        recipe_title = "Pantry Tomato Pasta"
        if utensil_available("microwave") and not utensil_available("stove"):
            recipe_steps = [
                {
                    "time": "0:00 Min",
                    "title": "Microwave Pasta",
                    "description": "Add pasta, water, and salt to a microwave-safe bowl. Microwave until pasta becomes soft.",
                    "icon": "fa-solid fa-mug-hot"
                },
                {
                    "time": "10:00 Min",
                    "title": "Make Sauce",
                    "description": "Add tomato, garlic, butter or oil, pepper, and herbs. Microwave again until sauce thickens.",
                    "icon": "fa-solid fa-fire"
                },
                {
                    "time": "18:00 Min",
                    "title": "Mix and Finish",
                    "description": "Add cheese or cream if available. Mix well and serve hot.",
                    "icon": "fa-solid fa-plate-wheat"
                }
            ]
        else:
            recipe_steps = [
                {
                    "time": "0:00 Min",
                    "title": "Boil Pasta",
                    "description": "Boil water with salt. Add pasta and cook until soft but firm. Drain and keep aside.",
                    "icon": "fa-solid fa-water"
                },
                {
                    "time": "10:00 Min",
                    "title": "Cook Tomato Sauce",
                    "description": "Heat oil or butter. Add garlic and onion. Add tomato, salt, pepper, chilli flakes, and herbs. Cook until thick.",
                    "icon": "fa-solid fa-fire"
                },
                {
                    "time": "20:00 Min",
                    "title": "Combine Pasta",
                    "description": "Add pasta to the sauce. Add cheese or cream if available. Toss well.",
                    "icon": "fa-solid fa-utensils"
                },
                {
                    "time": "25:00 Min",
                    "title": "Serve",
                    "description": "Serve hot with extra cheese or herbs.",
                    "icon": "fa-solid fa-plate-wheat"
                }
            ]

    elif has("paneer"):
        recipe_title = "Paneer Masala Skillet"
        recipe_steps = [
            {
                "time": "0:00 Min",
                "title": "Prepare Paneer",
                "description": "Cut paneer into cubes. Chop onion and tomato if available.",
                "icon": "fa-solid fa-cheese"
            },
            {
                "time": "8:00 Min",
                "title": "Cook Base",
                "description": "Heat oil or butter. Add onion, tomato, ginger-garlic paste, turmeric, chilli powder, and salt. Cook until soft.",
                "icon": "fa-solid fa-fire"
            },
            {
                "time": "18:00 Min",
                "title": "Add Paneer",
                "description": "Add paneer cubes and mix gently. Add a little water or cream and simmer for few minutes.",
                "icon": "fa-solid fa-pot-food"
            },
            {
                "time": "25:00 Min",
                "title": "Serve",
                "description": "Serve hot with roti, rice, or bread.",
                "icon": "fa-solid fa-plate-wheat"
            }
        ]

    elif has_any(["egg", "eggs"]):
        recipe_title = "Quick Egg Meal"
        recipe_steps = [
            {
                "time": "0:00 Min",
                "title": "Prepare Egg Mix",
                "description": "Beat eggs with salt, pepper, onion, tomato, and green chilli if available.",
                "icon": "fa-solid fa-egg"
            },
            {
                "time": "5:00 Min",
                "title": "Cook",
                "description": "Heat a pan with oil or butter. Pour the egg mixture and cook until set.",
                "icon": "fa-solid fa-fire"
            },
            {
                "time": "12:00 Min",
                "title": "Serve",
                "description": "Serve with bread, rice, or salad depending on your pantry.",
                "icon": "fa-solid fa-plate-wheat"
            }
        ]

    else:
        recipe_title = "All-In Pantry Skillet" if chef_mode == "all-in" else "Gourmet Pantry Bowl"
        recipe_steps = [
            {
                "time": "0:00 Min",
                "title": "Sort Ingredients",
                "description": f"Use these ingredients: {selected_display}. Wash and cut them into small pieces.",
                "icon": "fa-solid fa-utensils"
            },
            {
                "time": "8:00 Min",
                "title": "Start Cooking",
                "description": "Heat oil in a pan. Add onion, garlic, or available aromatics first for better flavour.",
                "icon": "fa-solid fa-fire"
            },
            {
                "time": "15:00 Min",
                "title": "Add Main Ingredients",
                "description": "Add harder ingredients first, then softer ingredients. Season with salt, pepper, and spices.",
                "icon": "fa-solid fa-carrot"
            },
            {
                "time": "25:00 Min",
                "title": "Finish",
                "description": "Cook until everything is tender. Taste and adjust seasoning before serving.",
                "icon": "fa-solid fa-circle-check"
            }
        ]

    if chef_mode == "all-in":
        recipe_steps.insert(1, {
            "time": "Mode",
            "title": "All-In Mode",
            "description": f"This mode uses all listed ingredients: {display_ingredients}. Add ingredients in cooking order: hard vegetables first, soft vegetables later, dairy or herbs at the end.",
            "icon": "fa-solid fa-layer-group"
        })
    else:
        recipe_steps.insert(1, {
            "time": "Mode",
            "title": "Gourmet Mode",
            "description": f"This mode uses the best matching ingredients: {selected_display}. Ingredients not used: {unused_display}.",
            "icon": "fa-solid fa-star"
        })

    if diet == "keto":
        recipe_steps.append({
            "time": "Diet",
            "title": "Keto Adjustment",
            "description": "Avoid rice, pasta, bread, potato, and sugar. Use paneer, egg, chicken, cheese, nuts, butter, olive oil, and low-carb vegetables.",
            "icon": "fa-solid fa-leaf"
        })
    elif diet == "vegan":
        recipe_steps.append({
            "time": "Diet",
            "title": "Vegan Adjustment",
            "description": "Avoid milk, butter, paneer, cheese, egg, chicken, fish, and meat. Use tofu, beans, lentils, vegetables, nuts, and plant-based milk.",
            "icon": "fa-solid fa-seedling"
        })
    elif diet == "vegetarian":
        recipe_steps.append({
            "time": "Diet",
            "title": "Vegetarian Adjustment",
            "description": "Avoid meat and fish. Use paneer, vegetables, lentils, beans, curd, and cheese based on your preference.",
            "icon": "fa-solid fa-carrot"
        })

    if goal == "weight loss":
        recipe_steps.append({
            "time": "Goal",
            "title": "Weight Loss Tip",
            "description": "Use less oil, reduce portion size, add more vegetables, and avoid fried toppings.",
            "icon": "fa-solid fa-heart-pulse"
        })
    elif goal == "weight gain":
        recipe_steps.append({
            "time": "Goal",
            "title": "Weight Gain Tip",
            "description": "Add nuts, paneer, cheese, avocado, ghee, olive oil, or whole grains to increase calories.",
            "icon": "fa-solid fa-bowl-food"
        })
    elif goal == "muscle gain":
        recipe_steps.append({
            "time": "Goal",
            "title": "Muscle Gain Tip",
            "description": "Increase protein using eggs, paneer, tofu, chicken, fish, lentils, beans, or Greek yogurt.",
            "icon": "fa-solid fa-dumbbell"
        })

    taste_atlas_match = {
        "region": cuisine,
        "dish_name": recipe_title,
        "description": (
            f"Generated from your pantry ingredients: {display_ingredients}. "
            f"Meal type: {meal_type.title()}, Time: {time_available} minutes, "
            f"Skill: {skill_level.title()}, Mode: {chef_mode.title()}."
        ),
        "link": f"https://www.tasteatlas.com/search?q={recipe_title.replace(' ', '+')}"
    }

    return render_template(
        'result.html',
        recipe_steps=recipe_steps,
        ingredients=display_ingredients,
        diet=diet,
        goal=goal,
        taste_atlas=taste_atlas_match
    )
if __name__ == '__main__':
    app.run(debug=True)