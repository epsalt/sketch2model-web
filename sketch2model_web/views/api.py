from sketch2model_web import app
from flask import request, jsonify, json

from sketch2model_web.sketch2model.image_processing import Sketch2Model
from sketch2model_web.utils import load_img, upload, array_to_img, S3_URL

@app.route("/api/heartbeat")
def api_heartbeat():
    """Health check for the API"""
    result = {
        "ok": True,
        "error": ""
    }
    return(jsonify(result))

@app.route("/api")
def api_sketch2model():
    try:
        url = request.args['url']
    except Exception as e:
        result = {
            "ok": False,
            "error": "url parameter not found"
        }
        return(jsonify(result))
    try:
        img = load_img(url)
    except OSError as e:
        result = {
            "ok": False,
            "error": "could not open image file"
            }
        return(jsonify(result))
    try:
        model = Sketch2Model(load_img(url))
        if(model.nregions == 1):
            result = {
                "ok": False,
                "error": "only identified one region in input image, try tuning parameters or simplify input image"
            }
        else:
            fname = upload(array_to_img(model.final), model = True)
            url = S3_URL(fname)
            result = {
                "ok": True,
                "url": url.modeled()
            }
        return(jsonify(result))
    except Exception as e:
        result = {
            "ok": False,
            "error": "image processing failed"
            }
        return(jsonify(result))
