from flask import Flask, render_template, request
import os
import cv2
import numpy as np

app = Flask(__name__)


def grade_matcha(image_path):
    
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    grade = None
    tip = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file part"
        else:
            file = request.files['file']
            if file.filename == '':
                error = "No selected file"
            else:
                filename = os.path.join('uploads', file.filename)
                os.makedirs('uploads', exist_ok=True)
                file.save(filename)

    return render_template('index.html', error=error, grade=grade, tip=tip)

if __name__ == '__main__':
    app.run(debug=True)
