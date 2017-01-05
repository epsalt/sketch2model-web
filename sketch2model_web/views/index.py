from flask import render_template, request, url_for
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
                   "contrast": form.get("contrast"),
                   "closing": form.get("closing"),
                   "cmap": form.get("cmap")}
        
        r = requests.get(url_for('api_sketch2model', _external=True),
                        params=payload).json()

        print(r)

        if r['ok'] == True:
            return render_template("app.html", sketch=url, model=r["url"])
        else:
            return render_template("app.html", error=r["error"])

    else:
        return render_template("app.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/intro")
def intro():
    return render_template("intro.html")
