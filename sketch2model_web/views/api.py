import base64

from flask import jsonify, request
from sketch2model_web import app
from sketch2model_web.sketch2model import Sketch2Model
from sketch2model_web.utils import array_to_img, load_img


@app.route("/api/heartbeat")
def api_heartbeat():
    """Health check for the API"""
    result = {"ok": True, "error": ""}
    return jsonify(result)


@app.route("/api", methods=["POST"])
def api_sketch2model():
    try:
        img = request.form["img"]
        contrast = float(request.form["contrast"])
        closing = int(request.form["closing"])
        cmap = request.form["cmap"]

    except Exception:
        result = {"ok": False, "url": "", "error": "url parameter not found"}
        return jsonify(result)

    try:
        img = load_img(img)

    except OSError:
        result = {"ok": False, "url": "", "error": "could not open image file"}
        return jsonify(result)

    try:
        model = Sketch2Model(img, contrast=contrast, closing=closing)

        if model.nregions == 1:
            result = {
                "ok": False,
                "img": "",
                "error": "only identified one region in input image, try tuning parameters or simplify input image",
            }

        else:
            img = array_to_img(model.final, cmap)
            result = {
                "ok": True,
                "img": base64.b64encode(img.read()).decode("ASCII"),
                "error": "",
            }
        return jsonify(result)

    except Exception as e:
        result = {"ok": False, "img": "", "error": str(e)}
        return jsonify(result)
