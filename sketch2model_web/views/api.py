from sketch2model_web import app
from flask import request, jsonify
from base64 import b64encode, b64decode
from io import BytesIO

from sketch2model_web.sketch2model.segment_5 import sketch2model


@app.route("/api/heartbeat")
def api_heartbeat():
    """Health check for the API"""

    result = {
        "ok": True,
        "error": ""
    }

    return jsonify(result)


@app.route("/api/sketch2model")
def api_sketch2model():
    """Main API view. Takes an image and runs  """

    try:
        sketch = b64decode(request.args.get('sketch'))
    except Exception as e:
        app.logger.error('API Sketch Error: %s', e)
        result = {
            'ok': False,
            'error': 'sketch not found or could not be opened'
        }
        return jsonify(result)

    try:
        buf = BytesIO()
        buf.write(sketch)
        buf.seek(0)
        model = sketch2model(buf).getvalue()
        model_b64 = b64encode(model).decode('utf-8')

    except Exception as e:
        app.logger.error('API Sketch2Model Error: %s', e)
        result = {
            'ok': False,
            'error': 'sketch2model image processing failed'
        }
        return jsonify(result)

    result = {
        'ok': True,
        'model': model_b64
    }
    return(jsonify(result))
