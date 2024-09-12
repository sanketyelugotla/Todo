from flask import Flask, render_template, request, redirect, flash, session
from pymongo import MongoClient
from datetime import datetime, timezone
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MongoDB connection setup
CONNECTION_STRING = "mongodb+srv://sanketyelugotla:sanket@sanket.m9hwme6.mongodb.net/?retryWrites=true&w=majority&appName=Sanket"
client = MongoClient(CONNECTION_STRING)
db = client.todoApp

# Collection names
todo_collection = db.todoAppCollection
login_collection = db.loginCollection


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        if login_collection.find_one({"username": username}) is None:
            password = request.form['password']
            user = {"username": username, "password": password}
            login_collection.insert_one(user)
            session['user'] = username
            flash("Account created and logged in successfully", 'success')
            return redirect("/logged")
        else:
            flash("User already exists", 'error')
    return render_template('signup.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop('user', None)
        username = request.form['username']
        user = login_collection.find_one({"username": username})
        if user and user['password'] == request.form['password']:
            session['user'] = username
            flash('Logged in successfully', 'success')
            return redirect('/logged')
        else:
            flash('Incorrect username or password', 'error')
    return render_template('login.html')


@app.route('/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.pop('user', None)
        flash('Logged out successfully', 'success')
        return redirect('/')
    return redirect('/')


@app.route('/logged', methods=["GET", "POST"])
def logged():
    if 'user' not in session:
        return redirect('/')

    username = session['user']
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = {
            "title": title,
            "desc": desc,
            "date_created": datetime.now(timezone.utc),
            "name": username
        }
        todo_collection.insert_one(todo)

    # Convert Cursor to List
    allTodo = list(todo_collection.find({"name": username}))
    return render_template('logged.html', allTodo=allTodo, username=username)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    return render_template('index.html')


@app.route('/delete/<int:sno>', methods=['GET', 'POST'])
def delete(sno):
    todo_collection.delete_one({"sno": sno})
    return redirect("/logged")


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo_collection.update_one(
            {"sno": sno},
            {"$set": {"title": title, "desc": desc}}
        )
        return redirect("/logged")

    todo = todo_collection.find_one({"sno": sno})
    return render_template('update.html', todo=todo)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
