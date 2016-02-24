import os
import time
from boto3 import resource
from werkzeug import secure_filename

from sketch2model_web import app
from sketch2model_web.sketch2model.segment_5 import sketch2model
from sketch2model_web.orientation import normalize_image_orientation

def allowed_file(filename):
    """Checks if a filename is in the set of allowed extensions specified
    in the app.config object."""

    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config["ALLOWED_EXTENSIONS"]

def generate_filename():
    """Generates a storage filename based on system time. Filenames
    are not random. Names match for both sketch and model."""
    return str(round(time.time(), 1)).replace(".", "")

def s3_put(file, filename, bucket, folder):
    """Convenience wrapper function for object upload to S3."""
    s3 = resource('s3')
    s3.Object(bucket, folder + '/' + filename).put(Body=file,
                                                   ContentType='image/jpeg')

def s3_get(filename, bucket, folder):
    """Convenience wrapper function for object download from S3."""
    s3 = resource('s3')
    return s3.Object(bucket, folder + '/' + filename).get()['Body']

def s3_url(filename, bucket, folder):
    """Builds a S3 object URL from components."""
    return "https://{bucket}.s3.amazonaws.com/{folder}/{filename}".format(
        bucket=bucket,
        folder=folder,
        filename=filename)

def upload_sketch(file, bucket, folder):
    """Validates user file from POST request and uploads to S3."""

    if allowed_file(file.filename):

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
        
        return upload_filename

def model_sketch(filename, bucket, upload_folder, model_folder):
    """Pulls sketch image from S3, runs sketch2model image processing
    on the image and then uploads result to S3."""
    sketch = s3_get(filename, bucket, upload_folder)
    model_object = sketch2model(sketch, filename)
    s3_put(model_object, filename, bucket, model_folder)
    model_object.close()
