from flask import render_template, render_template_string, request, redirect, url_for
from werkzeug import secure_filename
import requests

from sketch2model_web import app
from sketch2model_web.utils import upload, S3_URL

from sketch2model_web.sketch2model.image_processing import Sketch2Model
from sketch2model_web.utils import load_img, upload, array_to_img

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        f = request.files.get('uploaded_file')
        fname = upload(f, model = False)
        return redirect(url_for('uploaded', fname = fname))
    else:
        return render_template("app.html")

@app.route("/uploaded/<fname>", methods=['GET', 'POST'])
def uploaded(fname):
    if request.method == 'GET':
        if request.args.get('model_button'):
            ## Use our own api to run sketch2model on input image
            url = S3_URL(fname)
            r = requests.get(url_for('api_sketch2model', _external=True),
                             params={"url": url.uploaded()}).json()
            if(r["ok"] == True):
                modeled_url = r["url"]
                return render_template("app.html",
                                       uploaded_image=url.uploaded(),
                                       model_image=modeled_url)
            else:
                return render_template_string(r["error"])
        else:
            url = S3_URL(fname)
            return render_template("app.html", uploaded_image=url.uploaded())

    elif request.method == 'POST':
        f = request.files.get('uploaded_file')
        fname = upload(f, model = False)
        return redirect(url_for('uploaded', fname=fname))

@app.route("/about")
def about():
    return render_template("about.html")
