import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from sketch2model.segment_5 import sketch2model
import numpy

UPLOAD_FOLDER = './assets/'
SKETCH_FOLDER = './sketches/'
ALLOWED_EXTENSIONS = set(['jpg', 'png'])

application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config['SKETCH_FOLDER'] = SKETCH_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@application.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        print("UPLOADING")
        filename = upload()
        return(redirect(url_for('uploaded', filename=filename)))
    else:
        return(render_template("application.html"))
    
def upload():
    file = request.files.get('uploaded_file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        return(filename)
    
@application.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    if request.method == 'GET':
        if request.args.get('sketch_button'):
            return(sketch(filename))
        else:
            return(render_template("application.html", uploaded_image=url_for('uploaded_file', filename=filename)))
    elif request.method == 'POST':
        return(redirect(url_for('index'), code=307))
        
def sketch(filename):
    sketch_name = os.path.join(application.config['UPLOAD_FOLDER'], filename)
    model_name = os.path.join(application.config['SKETCH_FOLDER'], filename)
    sketch2model(sketch_name, model_name)
    #--- ---
    return(render_template("application.html", uploaded_image=url_for('uploaded_file', filename=filename),
                           sketched_image=url_for('sketched_file', filename=filename)))

@application.route("/uploads/<filename>")
def uploaded_file(filename):
     return(send_from_directory(application.config['UPLOAD_FOLDER'],
                                filename))
 
@application.route("/sketches/<filename>")
def sketched_file(filename):
    return(send_from_directory(application.config['SKETCH_FOLDER'],
                               filename))

@application.route("/about")
def about():
    return(render_template("about.html"))

if __name__ == "__main__":
      application.run()