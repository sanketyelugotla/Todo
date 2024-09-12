# For activating virtual environment ->./env/Scripts/activate.ps1

from flask import Flask, render_template, request, redirect, flash, session
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import re
import io
import zlib
from werkzeug.utils import secure_filename
from flask import Response
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
# from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import face_recognition
from PIL import Image
from base64 import b64encode, b64decode
import re
import base64
import shutil
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_BINDS'] = {
    'todo': 'sqlite:///todo.db',
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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


class Image(db.Model):
    __bind_key__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, unique=True, nullable=False)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        if Login.query.filter_by(username=username).first() is None:
            username = request.form['username']
            password = request.form['password']
            user = Login(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = username
            flash("Account created and logged In successfully", 'success')
            return redirect("/logged")
        else:
            flash("User already exists", 'error')


@app.route('/login', methods=["GET", "POST"])
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


@app.route('/logout', methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        session.pop('user', None)
        return redirect('/')
    flash('Logged out successfully', 'success')

    return redirect("/")


@app.route('/logged', methods=["GET", "POST"])
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


@app.route('/', methods=['GET', 'POST'])
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


# @app.route('/show')
# def products():
#     allTodo = Todo.query.all()
#     print(allTodo)
#     return 'This is products page!'


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/logged")


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
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


@app.route("/facereg", methods=["GET", "POST"])
def facereg():
    if request.method == "POST":
        session.pop('user', None)
        encoded_image = request.form.get("pic").encode('utf-8')
        username = request.form.get("name")

        user = Login.query.filter_by(username=username).first()
        if user is not None:
            temp_dir = 'static/temp/'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            temp_image_path = os.path.join(temp_dir, f'{username}_temp.jpg')
            with open(temp_image_path, 'wb') as temp_image:
                temp_image.write(b64decode(encoded_image))

            existing_image_path = f'static/face/{username}.jpg'
            # existing_image_path = 'static/face/sanket.jpg'
            print(existing_image_path)
            if not os.path.exists(existing_image_path):
                flash('No existing image found for user', 'error')
                os.remove(temp_image_path)  # Clean up the temporary file
                return redirect(request.url)  # Redirect back to the same page

            try:
                existing_image = face_recognition.load_image_file(
                    existing_image_path)
                temp_image = face_recognition.load_image_file(temp_image_path)

                existing_encoding = face_recognition.face_encodings(existing_image)[
                    0]
                temp_encoding = face_recognition.face_encodings(temp_image)[0]

                results = face_recognition.compare_faces(
                    [existing_encoding], temp_encoding)

                # Clean up the temporary file after comparison
                os.remove(temp_image_path)

                if results[0]:
                    session["user"] = username
                    flash('Login is successful', 'success')
                    return redirect("/logged")
                else:
                    flash('Faces do not match', 'error')
                    return redirect(request.url)
            except Exception as e:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                print(e)  # Useful for debugging
                flash('An error occurred processing the image', 'error')
                return redirect(request.url)
        else:
            flash('User not found', 'error')
            return redirect(request.url)
    else:
        return render_template("camera.html")


@app.route('/faceset', methods=['POST'])
def facset():
    # Get the username and image data from the form data
    username = request.form['name']
    image_data_url = request.form['pic']

    # Remove the header from the image data URL
    encoded_image_data = image_data_url.split(',')[1]

    # Decode base64-encoded image data
    binary_image_data = base64.b64decode(encoded_image_data)

    # Set the image path to 'static/face/name.jpg'
    image_dir = 'static/face/'
    # Create directory if it doesn't exist
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f'{username}.jpg')

    try:
        # Save the image
        with open(image_path, 'wb') as f:
            with BytesIO(binary_image_data) as b:
                shutil.copyfileobj(b, f)

        # Check if the file was actually written by verifying its existence
        if os.path.exists(image_path):
            return 'Image saved successfully.'
        else:
            return 'Image not saved. File does not exist.'

    except Exception as e:
        return f'Error saving image: {str(e)}'


# from app import app, db
# app.app_context().push()
# db.create_all(bind_key=[None,'todo'])
if __name__ == "__main__":
    app.run(debug=True, port=5000)
