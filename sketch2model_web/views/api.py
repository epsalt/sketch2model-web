from sketch2model_web import app
from flask import request, jsonify, make_response

from sketch2model_web.sketch2model.segment_5 import sketch2model


@app.route("/api/heartbeat")
def api_heartbeat():
    """Health check for the API"""

    result = {
        "ok": True,
        "error": ""
    }

    return jsonify(result)


@app.route("/api/sketch2model", methods=['POST'])
def api_sketch2model():
    """Main API: Takes an image, runs sketch2model image processing and
    returns model as a png image"""

    try:
        ## Add more validation here
        sketch = request.files['sketch']
    except Exception as e:
        app.logger.error('API Sketch Error: %s', e)
        result = {
            'ok': False,
            'error': 'sketch not found or could not be opened'
        }
        return jsonify(result)

    try:
        model = sketch2model(sketch)
        response = make_response(model.getvalue())
        response.mimetype = 'image/png'

    except Exception as e:
        app.logger.error('API Sketch2Model Error: %s', e)
        result = {
            'ok': False,
            'error': 'sketch2model image processing failed'
        }
        return jsonify(result)

    return(response)
