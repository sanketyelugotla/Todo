from flask import Flask, request, render_template
import os
import base64
import shutil
from io import BytesIO

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('read_camera.html')


@app.route('/facereg', methods=['POST'])
def facereg():
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


if __name__ == '__main__':
    app.run(debug=True)
