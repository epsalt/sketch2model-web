import os
import time
import logging

from sketch2model_web import app
from sketch2model.segment_5 import sketch2model
from utils.orientation import normalize_image_orientation

from boto3 import resource
from flask import render_template, request, redirect, url_for
from werkzeug import secure_filename


app.config['S3_BUCKET'] = 'sketch2model'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'gif', 'png'])


# Helper functions

def allowed_file(filename):
    """Checks if a filename is in the set of allowed extensions specified
    in the app.config object."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload(bucket, folder):
    """Validates user file from POST request and uploads to S3."""

    file = request.files.get('uploaded_file')
    if file and allowed_file(file.filename):

        # Strip extension off upload and generate new filename
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        upload_filename = generate_filename() + extension

        # Normalize jpegs with orientation tags
        if extension == ("jpeg" or "jpg"):
            file = normalize_image_orientation(file)
            s3_put(file, upload_filename, bucket, folder)
            file.close()
        else:
            s3_put(file, upload_filename, bucket, folder)
        
        return(upload_filename)


def s3_put(file, filename, bucket, folder):
    """Convenience wrapper function for object upload to S3."""
    s3 = resource('s3')
    s3.Object(bucket, folder + '/' + filename).put(Body=file,
                                                   ContentType='image/jpeg')


def s3_get(filename, bucket, folder):
    """Convenience wrapper function for object download from S3."""
    s3 = resource('s3')
    return(s3.Object(bucket, folder + '/' + filename).get()['Body'])


def s3_url(filename, bucket, folder):
    """Builds a S3 object URL from components."""
    return("https://{bucket}.s3.amazonaws.com/{folder}/{filename}".format(
        bucket=bucket,
        folder=folder,
        filename=filename))


def model(filename, bucket, upload_folder, model_folder):
    """Pulls sketch image from S3, runs sketch2model image processing
    on the image and then uploads result to S3."""
    sketch = s3_get(filename, bucket, upload_folder)
    model_object = sketch2model(sketch, filename)
    s3_put(model_object, filename, bucket, model_folder)
    model_object.close()


def generate_filename():
    """Generates a storage filename based on system time. Filenames
    are not random. Names match for both sketch and model."""
    return(str(round(time.time(), 1)).replace(".", ""))


# Routing

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        filename = upload(app.config['S3_BUCKET'],
                          app.config['UPLOAD_FOLDER'])
        return(redirect(url_for('uploaded', filename=filename)))
    else:
        return(render_template("app.html"))


@app.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    bucket = app.config['S3_BUCKET']
    upload_folder = app.config['UPLOAD_FOLDER']
    model_folder = app.config['MODEL_FOLDER']
    upload_url = s3_url(filename, bucket, upload_folder)
    model_url = s3_url(filename, bucket, model_folder)

    if request.method == 'GET':
        if request.args.get('model_button'):
            model(filename, bucket, upload_folder, model_folder)
            return(render_template("app.html", uploaded_image=upload_url,
                                   model_image=model_url))
        else:
            return(render_template("app.html", uploaded_image=upload_url))

    elif request.method == 'POST':
        filename = upload(app.config['S3_BUCKET'],
                          app.config['UPLOAD_FOLDER'])
        return(redirect(url_for('uploaded', filename=filename)))


@app.route("/about")
def about():
    return(render_template("about.html"))

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', error)
    return(render_template('500.html'), 500)

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return(render_template('500.html'), 500)

