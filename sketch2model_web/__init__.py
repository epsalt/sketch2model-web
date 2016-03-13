from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from sketch2model_web.views import index
from sketch2model_web.views import errors
from sketch2model_web.views import api
