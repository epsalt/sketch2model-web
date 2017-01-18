from flask import redirect, render_template, request, jsonify, url_for
import requests

from sketch2model_web import app
from sketch2model_web.utils import upload, s3_url

@app.route("/app", methods=['GET'])
def index():
    return render_template("app.html")

@app.route("/app/post", methods=['POST'])
def app_post():
    form = request.form

    if form.get("options") == "example":
        ex_name = form.get("example")
        url = s3_url(ex_name + ".png").get('example')

    else:
        f = request.files['upload']

        if f.filename == "":
            r = {"ok": False,
                 "url": "",
                 "error": "No selected file"}

            return jsonify(r)

        try:
            fname = upload(f, model=False)

        except ValueError:
            error = "Sketch2Model does not accept this filetype, try again with jpg, gif or png"
            r = {"ok": False,
                 "url": "",
                 "error": error}

            return jsonify(r)

        url = s3_url(fname).get('uploaded')

    payload = {"url": url,
               "example": form.get("example"),
               "contrast": form.get("contrast"),
               "closing": form.get("closing"),
               "cmap": form.get("cmap")}

    r = requests.get(url_for('api_sketch2model', _external=True),
                    params=payload).json()

    return jsonify(r)

@app.route("/")
def intro():
    return render_template("intro.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api_reference")
def api_reference():
    return render_template("api_reference.html")
