import re
import os
import uuid

from celery.result import AsyncResult
from flask import Flask, redirect, render_template, request, send_from_directory
from flask_celery import make_celery
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from werkzeug.utils import secure_filename

import config


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % app.config['POSTGRES']


db = SQLAlchemy(app)
celery = make_celery(app)


class Results(db.Model):
    uuid = db.Column(db.String(55), primary_key=True)
    text = db.Column(db.String(50))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        filename, file_extention = os.path.splitext(file_path)
        uuid_filename = str(uuid.uuid4()) + file_extention
        uuid_file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], uuid_filename)
        file.save(uuid_file_path)
        return redirect('/process/' + uuid_filename)


@app.route('/process/<filename>')
def task_processing(filename):
    task = processing.delay(filename)
    async_result = AsyncResult(id=task.task_id, app=celery)
    processing_result = async_result.get()
    return render_template('result.html', image_name=processing_result)


@app.route('/result/<filename>')
def send_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@celery.task(name='qkr.processing')
def processing(filename):
    image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    new_image = image.resize((400, 400))
    new_image_filename = '_' + filename
    new_image_filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_image_filename)
    new_image.save(new_image_filepath)
    return new_image_filename

if __name__ == '__main__':
    app.run()