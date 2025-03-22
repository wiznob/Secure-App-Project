from flask import Flask, request, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
import sqlite3
import bcrypt  #password hashing
import bleach  #input sanitization
import re

app = Flask(__name__)
app.secret_key = 'I8{7?lrJne2aAE8Fs_0R'
csrf = CSRFProtect(app)

# Making database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

@app.route("/")
def welcome():
    return redirect(url_for('register'))

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return  "the username or password is empty. Please try again"
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        #using parameterized query to stop SQL injection
        query = "SELECT password FROM users WHERE username = ?"
        c.execute(query, (username,))
        result = c.fetchone()
        conn.close()
        #verifying hashed password
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
            return redirect(url_for('home', username=username))
        else:
            return "Invalid credentials. Try again."

    return render_template("login.html")

#register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            return "the username or password is empty. Please try again"
        #Check if password exist already
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        query = "SELECT * FROM users WHERE username = ?"
        c.execute(query, (username,))
        if c.fetchone():
            conn.close()
            return "Username already exists. Please try another."
        #check the password strength
        if not re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', password):
            conn.close()
            return "Password must be at least 8 characters long and contain at least one letter and one number. and one special symbol"
        #sanitizing username input to block a potential XSS attack
        username = bleach.clean(username)
        #Using hashing on the password then storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        #now passwords are hashed we can store them
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/home")
def home():
    #load homepage
    username = request.args.get("username")
    return render_template("home.html", username=username)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
