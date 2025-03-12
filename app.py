from flask import Flask, render_template, request, redirect, url_for
import sqlite3

import os
from werkzeug.utils import secure_filename
# Flask is a Python web framework that makes it easy to build web applications. 
# It provides tools and libraries for routing, rendering templates, handling forms, and interacting with databases.


# render_template: This function is used to render HTML templates in the response.
# request: This object contains data from incoming HTTP requests (such as form submissions).
# redirect: This function is used to redirect a user to a different route (URL).
# url_for: This function generates a URL for a given view function (e.g., for redirecting).
# sqlite3: A Python module that allows interaction with SQLite databases. 
# SQLite is a lightweight relational database engine, ideal for small-scale applications like this one.


# Flask Application Instance (app): The Flask class creates an application instance. 
# The __name__ argument tells Flask where to look for application resources (templates, static files, etc.).

app = Flask(__name__)


UPLOAD_FOLDER = "\\static\\uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
def init_db():
    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT, 
                            points INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS recycling (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER, 
                            item TEXT, 
                            points INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS dogs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT, 
                            breed TEXT, 
                            age INTEGER, 
                            description TEXT,
                            image_url TEXT)''')
                # New table for adoptions
        cursor.execute('''CREATE TABLE IF NOT EXISTS adoptions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_name TEXT,
                            email TEXT,
                            phone TEXT,
                            dog_id INTEGER,
                            dog_name TEXT,
                            FOREIGN KEY (dog_id) REFERENCES dogs(id))''')

        # Insert sample dogs if the table is empty
        cursor.execute("SELECT COUNT(*) FROM dogs")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO dogs (name, breed, age, description,image_url) VALUES (?, ?, ?, ?,?)", 
                               [
                ("Buddy", "Golden Retriever", 3, "Friendly and playful.", "/static/images/buddy.jpg"),
                ("Luna", "Labrador", 2, "Loves to cuddle.","/static/images/luna.jpg"),
                ("Charlie", "Beagle", 4, "Very energetic and curious.","/static/images/charlie.jpg")
            ]
            )
        
        conn.commit()

@app.route('/add_dog', methods=['POST'])
def add_dog():
    name = request.form['name']
    breed = request.form['breed']
    age = request.form['age']
    description = request.form['description']
    print("heree2!")

    # Handle file upload
  # Securely handle file upload
    photo = request.files.get('image_url')  # Avoid KeyError
    print(request.files) 
    print(photo)

    if photo and photo.filename:  # Ensure a file was uploaded
        print("inside save")
        filename = secure_filename(photo.filename)
        
        print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      #  path_x = "C:\Users\thstergiou\Desktop\My_Workspace\\projects\\python_lessons\\Project"
        photo.save(path_x+app.config['UPLOAD_FOLDER'], filename)
    else:
        filename = 'default.jpg'  # Fallback if no file is uploaded


    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dogs (name, breed, age, description) VALUES (?, ?, ?, ?)", 
                       (name, breed, age, description))
        conn.commit()

    return redirect(url_for('home'))




@app.route('/')
def home():
    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dogs")
        dogs = cursor.fetchall()
    return render_template('index.html', dogs=dogs)

@app.route('/adopt/<int:dog_id>')
def adopt_dog(dog_id):
    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dogs WHERE id = ?", (dog_id,))
        dog = cursor.fetchone()
    if dog:
        return render_template('adopt.html', dog=dog)
    else:
        return "Dog not found", 404
    
@app.route('/adopt_dog', methods=['POST'])
def adopt_dog_form():
    user_name = request.form['user_name']
    email = request.form['email']
    phone = request.form['phone']
    dog_id = request.form['dog_id']
    dog_name = request.form['dog_name']

    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO adoptions (user_name, email, phone, dog_id, dog_name) VALUES (?, ?, ?, ?, ?)",
                       (user_name, email, phone, dog_id, dog_name))
        conn.commit()

    return redirect(url_for('home'))


@app.route('/admin/adoptions')
def admin_adoptions():
    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM adoptions")
        adoptions = cursor.fetchall()
    return render_template('admin.html', adoptions=adoptions)

@app.route('/admin/delete_adoption/<int:adoption_id>', methods=['POST'])
def delete_adoption(adoption_id):
    with sqlite3.connect("recycle_for_paws.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM adoptions WHERE id = ?", (adoption_id,))
        conn.commit()
    return redirect(url_for('admin_adoptions'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
