import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug import secure_filename
from PIL import Image
import PIL.ImageOps

UPLOAD_FOLDER = './assets/'
SKETCH_FOLDER = './sketches/'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SKETCH_FOLDER'] = SKETCH_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request.method)
    if request.method == 'POST':
        file = request.files.get('uploaded_file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return(redirect(url_for('uploaded', filename=filename)))
    else:
        return(render_template("app.html"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
     return(send_from_directory(app.config['UPLOAD_FOLDER'],
                                filename))

@app.route("/sketches/<filename>")
def sketched_file(filename):
    return(send_from_directory(app.config['SKETCH_FOLDER'],
                               filename))

@app.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    if request.method == 'GET' and request.args.get('sketch_button'):
        # Image processing goes here
        image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        inverted_image = PIL.ImageOps.invert(image)
        inverted_image.save(os.path.join(app.config['SKETCH_FOLDER'], filename))

        # Render template with original image and sketch
        return(render_template("app.html", uploaded_image=url_for('uploaded_file', filename=filename),
                               sketched_image=url_for('sketched_file', filename=filename)))
    return(render_template("app.html",uploaded_image=url_for('uploaded_file', filename=filename)))
    
@app.route("/about")
def about():
    return(render_template("about.html"))

if __name__ == "__main__":
    app.debug = True
    app.run()
