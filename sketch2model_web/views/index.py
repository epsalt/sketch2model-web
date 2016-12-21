from flask import render_template, render_template_string, request, redirect, url_for
from werkzeug import secure_filename
import requests

from sketch2model_web import app
from sketch2model_web.utils import upload, s3_url

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
            uploaded_url = s3_url(fname, model = False)
            r = requests.get(url_for('api_sketch2model', _external=True),
                             params={"url": uploaded_url})
            
            model_url = r.json()["url"]
            return render_template("app.html",
                uploaded_image=s3_url(fname, model = False),
                model_image=model_url)
        else:
            upload_url = s3_url(fname, model = False)
            return render_template("app.html", uploaded_image=upload_url)

    elif request.method == 'POST':
        f = request.files.get('uploaded_file')
        fname = upload(f, model = False)
        return redirect(url_for('uploaded', fname=fname))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test")
def test():
    r = requests.get(url_for('api_heartbeat', _external=True))
    data = r.json()
    test = data["ok"]
    return render_template_string(str(test))
