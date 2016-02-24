from flask import render_template, request, redirect, url_for

from sketch2model_web import app
from sketch2model_web.sketch2model.segment_5 import sketch2model
from sketch2model_web.utils import allowed_file, generate_filename, \
    s3_put, s3_get, s3_url, model_sketch, upload_sketch


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('uploaded_file')
        filename = upload_sketch(file, app.config['S3_BUCKET'],
                          app.config['UPLOAD_FOLDER'])
        return redirect(url_for('uploaded', filename=filename))
    else:
        return render_template("app.html")

@app.route("/uploaded/<filename>", methods=['GET', 'POST'])
def uploaded(filename):
    bucket = app.config['S3_BUCKET']
    upload_folder = app.config['UPLOAD_FOLDER']
    model_folder = app.config['MODEL_FOLDER']
    upload_url = s3_url(filename, bucket, upload_folder)
    model_url = s3_url(filename, bucket, model_folder)

    if request.method == 'GET':
        if request.args.get('model_button'):
            model_sketch(filename, bucket, upload_folder, model_folder)
            return render_template("app.html", uploaded_image=upload_url,
                                   model_image=model_url)
        else:
            return render_template("app.html", uploaded_image=upload_url)

    elif request.method == 'POST':
        file = request.files.get('uploaded_file')
        filename = upload_sketch(file, app.config['S3_BUCKET'],
                          app.config['UPLOAD_FOLDER'])
        return redirect(url_for('uploaded', filename=filename))

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', error)
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', e)
    return render_template('500.html'), 500

