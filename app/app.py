import cv2
import logging
import os
import uuid
import yaml
from collections import Counter
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename

from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from flask import Flask, redirect, render_template, request, send_from_directory
from flask_celery import make_celery

config_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "config.yml"))
config = yaml.load(open(config_path))

app = Flask(__name__)
app.config.update(config)

celery = make_celery(app)

logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(app.config['LOGFILE'])
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


def set_logger(logger):
    """Setup logger."""
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = set_logger(logger)
celery_logger = set_logger(celery_logger)


@app.route('/')
def index():
    """Start page."""
    return render_template('index.html')


def allowed_file(filename):
    """Check format of the file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
def upload():
    """Upload file endpoint."""
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

        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        filename, file_extension = os.path.splitext(path)

        # Set the uploaded file a uuid name
        filename_uuid = str(uuid.uuid4()) + file_extension
        path_uuid = os.path.abspath(os.path.join(os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], filename_uuid))

        file.save(path_uuid)
        logger.info(f'the file {file.filename} has been successfully saved as {filename_uuid}')
        return redirect('/process/' + filename_uuid)


@app.route('/process/<filename>')
def task_processing(filename):
    """Process the image endpoint."""
    task = processing.delay(filename)
    async_result = AsyncResult(id=task.task_id, app=celery)
    processing_result = async_result.get()
    return render_template('result.html', image_name=processing_result)


@app.route('/result/<filename>')
def send_image(filename):
    """Show result endpoint."""
    return send_from_directory(os.path.abspath(os.path.join(os.getcwd(), os.pardir, app.config['RESULT_FOLDER'])),
                               filename)


def rgb2hex(rgb):
    """Convert color code from RGB to HEX."""
    hex_code = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex_code


@celery.task(name='celery.processing')
def processing(filename):
    """Celery function for the image processing."""
    colors_number = 6
    celery_logger.info(f'{filename} is processing : colors_number={colors_number}')
    path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], filename))

    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    resized_img_rgb = cv2.resize(img_rgb, (64, 64), interpolation=cv2.INTER_AREA)

    img_list = resized_img_rgb.reshape((resized_img_rgb.shape[0] * resized_img_rgb.shape[1], 3))

    clt = KMeans(n_clusters=colors_number)
    labels = clt.fit_predict(img_list)

    label_counts = Counter(labels)

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

    file_path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, app.config['RESULT_FOLDER'], filename))
    plt.savefig(file_path)
    celery_logger.info(f'processing {filename} is completed : {color_labels}')
    return filename


if __name__ == "__main__":
    app.run(host="0.0.0.0")
