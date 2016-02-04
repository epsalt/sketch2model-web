import os
import boto3
import time
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from sketch2model.segment_5 import sketch2model

app = Flask(__name__)
app.config['S3_BUCKET'] = 'sketch2model'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SKETCH_FOLDER'] = 'sketches'
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
        s3 = boto3.resource('s3')
        s3.Object(bucket, folder + '/'+
                  upload_filename).put(Body=file,
                                       ContentType='image/jpeg',
                                       ACL='public-read')
        # Generate URL
        url = "https://{bucket}.s3.amazonaws.com/{folder}/{fname}".format(
            bucket = bucket,
            folder = folder,
            fname  = upload_filename)
        return(url)

def sketch(filename):
    sketch_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    model_name = os.path.join(app.config['SKETCH_FOLDER'], filename)
    sketch2model(sketch_name, model_name)
    return(render_template("app.html", uploaded_image=url_for('uploaded_file', filename=filename),
                           sketched_image=url_for('sketched_file', filename=filename)))

def generate_filename():
    return(str(round(time.time(), 1)).replace(".", ""))

## Routing
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = upload(app.config['S3_BUCKET'], app.config['UPLOAD_FOLDER'])
        return(url)
        return(redirect(url_for('uploaded', filename=filename)))
    else:
        return(render_template("app.html"))

@app.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    if request.method == 'GET':
        if request.args.get('sketch_button'):
            return(sketch(filename))
        else:
            return(render_template("app.html", uploaded_image=url_for('uploaded_file', filename=filename)))
    elif request.method == 'POST':
        return(redirect(url_for('index'), code=307))
        
@app.route("/uploads/<filename>")
def uploaded_file(filename):
     retuasdfrn(send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename))
 
@app.route("/sketches/<filename>")
def sketched_file(filename):
    return(send_from_directory(app.config['SKETCH_FOLDER'],
                               filename))

@app.route("/about")
def about():
    return(render_template("about.html"))

if __name__ == "__main__":
    app.run(debug=True)
