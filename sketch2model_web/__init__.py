from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from sketch2model_web.views import general
from sketch2model_web.views import errors
