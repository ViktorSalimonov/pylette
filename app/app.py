import os

from flask import Flask, redirect, render_template, request
from flask_celery import make_celery
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import config


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)
celery = make_celery(app)

class Task(db.Model):
    pass





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(file_path)
        return redirect('/')

if __name__ == '__main__':
    app.run()