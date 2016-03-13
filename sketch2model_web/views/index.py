from flask import render_template, request, redirect, url_for
from werkzeug import secure_filename

from sketch2model_web import app
from sketch2model_web.utils import s3_url, model_sketch, upload_sketch

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('uploaded_file')
        ext = secure_filename(file.filename).rsplit('.', 1)[1]        
        if ext in app.config['ALLOWED_EXTENSIONS']:
            new_filename = upload_sketch(file, ext,
                                         app.config['S3_BUCKET'],
                                         app.config['UPLOAD_FOLDER'])
        return redirect(url_for('uploaded', filename=new_filename))
    else:
        return render_template("app.html")

@app.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    upload_url = s3_url(filename, app.config['S3_BUCKET'],
                        app.config['UPLOAD_FOLDER'])
    model_url = s3_url(filename, app.config['S3_BUCKET'],
                       app.config['MODEL_FOLDER'])

    if request.method == 'GET':
        if request.args.get('model_button'):
            model_sketch(filename, app.config['S3_BUCKET'],
                         app.config['UPLOAD_FOLDER'],
                         app.config['MODEL_FOLDER'])
            return render_template("app.html", uploaded_image=upload_url,
                                   model_image=model_url)
        else:
            return render_template("app.html", uploaded_image=upload_url)

    elif request.method == 'POST':
        file = request.files.get('uploaded_file')
        ext = secure_filename(file.filename).rsplit('.', 1)[1]        
        if ext in app.config['ALLOWED_EXTENSIONS']:
            new_filename = upload_sketch(file, ext,
                                         app.config['S3_BUCKET'],
                                         app.config['UPLOAD_FOLDER'])
        return redirect(url_for('uploaded', filename=new_filename))

@app.route("/about")
def about():
    return render_template("about.html")
