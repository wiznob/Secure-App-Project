from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

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
    return redirect(url_for('home'))

#login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        #SQl Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        c.execute(query)
        result = c.fetchone()
        conn.close()
        if result:
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
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        #keeping passwords in plaintext
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        #move to login after registered
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route("/home")
def home():
    #load homepage
    return render_template("home.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)