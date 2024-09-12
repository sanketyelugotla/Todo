# For activating virtual environment ->./env/Scripts/activate.ps1

from flask import Flask, render_template, request, redirect, flash, session
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from face import face_recog
app2 = Flask(__name__)
app2.secret_key = os.urandom(24)

app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app2.config['SQLALCHEMY_BINDS'] = {
    'todo': 'sqlite:///todo.db'
}
app2.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app2)


class Todo(db.Model):
    __bind_key__ = 'todo'
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


class Login(db.Model):
    username = db.Column(db.String(20), nullable=False, primary_key=True)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f"{self.username} - {self.password}"


@app2.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        if Login.query.filter_by(username=username).first() is None:
            db_uri = 'sqlite:///' + username + '.db'
            print("Database URI:", db_uri)  # Print database URI for debugging
            app2.config['SQLALCHEMY_DATABASE_URI'] = db_uri
            try:
                db.create_all()
                # Print success message for table creation
                print("Tables created successfully")
                password = request.form['password']
                user = Login(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                session['user'] = username
                flash("Account created and logged In successfully", 'success')
                return redirect("/logged")
            except Exception as e:
                flash("Error creating account: " + str(e), 'error')
                # Print error message for debugging
                print("Error creating tables:", e)
        else:
            flash("User already exists", 'error')
    return redirect("/")


@app2.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop('user', None)
        username = request.form['username']
        if Login.query.filter_by(username=username).first() is not None:
            password = request.form['password']
            search = Login.query.filter_by(username=username).first()
            if (username == search.username and password == search.password):
                session['user'] = username
                # return render_template('logged.html', username=username)
                flash('Logged in Successfully', 'success')
                return redirect('logged')
            else:
                flash('Incorrect Password', 'error')
        else:
            flash('User not found', 'error')

    return redirect("/")


@app2.route('/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.pop('user', None)
        return redirect('/')
    flash('Logged out successfully', 'success')

    return redirect("/")


@app2.route('/logged', methods=["GET", "POST"])
def logged():
    if 'user' not in session:
        return redirect('/')
    else:
        username = session['user']
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            name = username
            todo = Todo(title=title, desc=desc, name=name)
            db.session.add(todo)
            db.session.commit()
        # allTodo = Todo.query.all()
        allTodo = Todo.query.filter_by(name=username).all()
        print(allTodo)
        return render_template('logged.html', allTodo=allTodo, username=username)


@app2.route('/', methods=['GET', 'POST'])
def hello_world():
    # return 'Hello, World!'
    if request.method == 'POST':
        if 'user' not in session:
            flash('Please Login to proceed', 'error')

    #     title = request.form['title']
    #     desc = request.form['desc']
    #     name = "some"
    #     todo = Todo(title=title, desc=desc, name=name)
    #     db.session.add(todo)
    #     db.session.commit()
    # # allTodo = Todo.query.all()
    # allTodo = Todo.query.filter_by(name="some").all()
    # # print(allTodo)

    return render_template('index.html')


@app2.route('/face', methods=['GET', 'POST'])
def face():
    face_recog()
    return "Hello"


# @app.route('/show')
# def products():
#     allTodo = Todo.query.all()
#     print(allTodo)
#     return 'This is products page!'


@app2.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/logged")


@app2.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/logged")

    todo = allTodo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)


# from app import app, db
# app.app_context().push()
# db.create_all(bind_key=[None,'todo'])

if __name__ == "__main__":
    app2.run(debug=True, port=5000)
