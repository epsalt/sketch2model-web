import os
from boto3 import resource
import time
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from sketch2model.segment_5 import sketch2model

app = Flask(__name__)
app.config['S3_BUCKET'] = 'sketch2model'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = 'models'
ALLOWED_EXTENSIONS = set(['jpg', 'png'])

## Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload(bucket, folder):
    file = request.files.get('uploaded_file')
    if file and allowed_file(file.filename):
        
        # Strip extension off upload and generate new filename
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1]
        upload_filename = generate_filename() + extension

        # Upload image to s3
        s3_put(file, upload_filename, bucket, folder)
        return(upload_filename)

def s3_put(file, filename, bucket, folder):
    s3 = resource('s3')
    s3.Object(bucket, folder + '/' + filename).put(Body=file,
                                                   ContentType='image/jpeg',
                                                   ACL='public-read')

def s3_get(filename, bucket, folder):
    s3 = resource('s3')
    return(s3.Object(bucket, folder + '/' + filename).get()['Body'])

def s3_url(filename, bucket, folder):
    return("https://{bucket}.s3.amazonaws.com/{folder}/{filename}".format(
        bucket  = bucket,
        folder  = folder,
        filename = filename))

def model(filename, bucket, upload_folder, model_folder):
    sketch = s3_get(filename, bucket, upload_folder)
    model_object = sketch2model(sketch, filename)
    s3_put(model_object, filename, bucket, model_folder)
    model_object.close()

def generate_filename():
    return(str(round(time.time(), 1)).replace(".", ""))

## Routing
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
    model_url  = s3_url(filename, bucket, model_folder)
    
    if request.method == 'GET':
        if request.args.get('model_button'):
            model(filename, bucket, upload_folder, model_folder)
            return(render_template("app.html", uploaded_image = upload_url,
                                   model_image=model_url))
        else:
            return(render_template("app.html", uploaded_image = upload_url))

    elif request.method == 'POST':
        return(redirect(url_for('index'), code=307))

@app.route("/about")
def about():
    return(render_template("about.html"))

if __name__ == "__main__":
    app.run(debug=True)
