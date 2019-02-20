from collections import Counter
import re
import os
import uuid

import cv2
from celery.result import AsyncResult
from flask import Flask, redirect, render_template, request, send_from_directory
from flask_celery import make_celery
from flask_sqlalchemy import SQLAlchemy
from matplotlib import pyplot as plt
from PIL import Image
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename

import config


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % app.config['POSTGRES']


db = SQLAlchemy(app)
celery = make_celery(app)


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


def rgb2hex(rgb):
    hex = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex


@celery.task(name='qkr.processing')
def processing(filename):
    k = 6
    path = os.path.join(
            app.config['UPLOAD_FOLDER'], filename)
    
    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    resized_img_rgb = cv2.resize(img_rgb, (64, 64), interpolation=cv2.INTER_AREA)

    img_list = resized_img_rgb.reshape((resized_img_rgb.shape[0] * resized_img_rgb.shape[1], 3))

    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(img_list)
        
    label_counts = Counter(labels)
    total_count = sum(label_counts.values())

    center_colors = list(clt.cluster_centers_)
    ordered_colors = [center_colors[i]/255 for i in label_counts.keys()]
    color_labels = [rgb2hex(ordered_colors[i]*255) for i in label_counts.keys()]
    
    plt.figure(figsize=(14, 8))
    plt.subplot(221)
    plt.imshow(img_rgb)
    plt.axis('off')

    plt.subplot(222)
    plt.pie(label_counts.values(), labels=color_labels, colors=ordered_colors, startangle=90)
    plt.axis('equal')
    file_path = os.path.join(
            app.config['UPLOAD_FOLDER'], '_'+filename)
    plt.savefig(file_path)
    return '_'+filename


if __name__ == '__main__':
    app.run()