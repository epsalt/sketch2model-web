from flask import render_template, render_template_string, redirect, request, url_for
import requests

from sketch2model_web import app
from sketch2model_web.utils import upload, s3_url

@app.route("/app", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        form = request.form

        if form.get("options") == "example":
            ex_name = form.get("example")
            url = s3_url(ex_name + ".png").get('example')

        else:
            f = request.files['upload']
            fname = upload(f, model=False)
            url = s3_url(fname).get('uploaded')

        payload = {"url": url,
                   "example": form.get("example"),
                   "contrast": form.get("contrast"),
                   "closing": form.get("closing"),
                   "cmap": form.get("cmap")}

        r = requests.get(url_for('api_sketch2model', _external=True),
                        params=payload).json()

        if r['ok'] == True:
            return render_template("app.html", sketch=url, model=r["url"],
                                   default=form)

        else:
            return render_template("app.html", error=r["error"],
                                   default=form)

    else:
        default_params = {"example": "Breaks",
                          "contrast": 0.5,
                          "closing": 3,
                          "cmap": "Pastel2",
                          "options": "example"}
        return render_template("app.html", default=default_params)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/")
def intro():
    return render_template("intro.html")
