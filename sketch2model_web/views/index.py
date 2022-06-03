import base64
import io

import requests
from flask import current_app, jsonify, render_template, request, url_for
from sketch2model_web import app
from sketch2model_web.utils import allowed_file
from werkzeug.datastructures import FileStorage


@app.route("/", methods=["GET"])
def index():
    return render_template("app.html")


@app.route("/app/post", methods=["POST"])
def app_post():
    form = request.form

    if form.get("options") == "example":
        ex_name = form.get("example")
        fname = ex_name + ".png"
        with current_app.open_resource("static/" + fname) as example:
            buf = io.BytesIO(example.read())
            f = FileStorage(buf, fname)

    else:
        f = request.files["upload"]

        if f.filename == "":
            r = {
                "ok": False,
                "error": "No selected file. Please select an image file or use one of our examples.",
            }

            return jsonify(r)

        if not allowed_file(f.filename):
            error = "Sketch2Model does not accept this filetype. Please try again with a jpg, gif or png."
            r = {"ok": False, "error": error}

            return jsonify(r)

    payload = {
        "img": base64.b64encode(f.read()).decode("ASCII"),
        "example": form.get("example"),
        "contrast": form.get("contrast"),
        "closing": form.get("closing"),
        "cmap": form.get("cmap"),
    }

    r = requests.post(url_for("api_sketch2model", _external=True), data=payload).json()

    return jsonify(r)
