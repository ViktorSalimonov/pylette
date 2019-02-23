from collections import Counter
import logging
import re
import os
import uuid

import cv2
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_celery import make_celery
from matplotlib import pyplot as plt
from PIL import Image
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename

import config


logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

logger.setLevel(logging.DEBUG)
celery_logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('/home/salv/Projects/qkr/app/app.log')
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
celery_logger.addHandler(file_handler)
celery_logger.addHandler(stream_handler)


app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)

celery = make_celery(app)


@app.route('/')
def index():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if not request.files.get('file', None):
            msg = 'the request contains no file'
            logger.error(msg)
            return render_template('exception.html', text=msg)
        
        file = request.files['file']
        if file and not allowed_file(file.filename):
            msg = f'the file {file.filename} has wrong extention'
            logger.error(msg)
            return render_template('exception.html', text=msg)
        
        path = os.path.join(
            app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        filename, file_extention = os.path.splitext(path)
        filename_uuid = str(uuid.uuid4()) + file_extention
        path_uuid = os.path.join(app.config['UPLOAD_FOLDER'], filename_uuid)
        
        file.save(path_uuid)
        logger.info(f'the file {file.filename} has been successfully saved as {filename_uuid}')
        return redirect('/process/' + filename_uuid)


@app.route('/process/<filename>')
def task_processing(filename):
    task = processing.delay(filename)
    async_result = AsyncResult(id=task.task_id, app=celery)
    processing_result = async_result.get()
    return render_template('result.html', image_name=processing_result)


@app.route('/result/<filename>')
def send_image(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


def rgb2hex(rgb):
    hex = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex


@celery.task(name='qkr.processing')
def processing(filename):
    celery_logger.info(f'working on the {filename} processing')
    k = 6
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
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

    file_path = os.path.join(app.config['RESULT_FOLDER'], filename)
    plt.savefig(file_path)
    return filename


if __name__ == '__main__':
    app.run()