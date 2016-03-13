import os
import time
from boto3 import resource

from sketch2model_web import app
from sketch2model_web.sketch2model.segment_5 import sketch2model
from sketch2model_web.orientation import normalize_image_orientation

def s3_url(filename, bucket, folder):
    """Builds a S3 object URL from components."""
    return "https://{bucket}.s3.amazonaws.com/{folder}/{filename}".format(
        bucket=bucket,
        folder=folder,
        filename=filename)

def generate_filename():
    """Generates a storage filename based on system time. Filenames
    are not random. Names match for both sketch and model."""
    return str(round(time.time(), 1)).replace(".", "")

def upload_sketch(file, ext, bucket, folder):

    new_filename = generate_filename() + '.' + ext
    s3 = resource('s3').Object(bucket, folder + '/' + new_filename)
    
    # Normalize jpegs with orientation tags
    if ext == ("jpeg" or "jpg"):
        file = normalize_image_orientation(file)
        s3.put(Body = file, ContentType = 'image/jpeg')
        file.close()
    else:
        s3.put(Body = file, ContentType = 'image/jpeg')

    return(new_filename)

def model_sketch(filename, bucket, upload_folder, model_folder):
    """Pulls sketch image from S3, runs sketch2model image processing
    on the image and then uploads result to S3."""
    s3 = resource('s3')
    
    s3_upload = s3.Object(bucket, upload_folder + '/' + filename)    
    sketch = s3_upload.get()['Body']

    s3_model = s3.Object(bucket, model_folder + '/' + filename)
    model_object = sketch2model(sketch)
    s3_model.put(Body=model_object, ContentType='image/jpeg') 
    model_object.close()
