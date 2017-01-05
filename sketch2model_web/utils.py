import requests
import io
import PIL
import time
from boto3 import resource

from sketch2model_web import app
from matplotlib import cm, colors

bucket = app.config['S3_BUCKET']
upload_folder = app.config['UPLOAD_FOLDER']
model_folder = app.config['MODEL_FOLDER']
example_folder = app.config['EXAMPLE_FOLDER']

def s3_url(fname):
    url = "https://{0}.s3.amazonaws.com/{1}/{2}"
    return {"uploaded": url.format(bucket, upload_folder, fname),
            "modeled": url.format(bucket, model_folder, fname),
            "example": url.format(bucket, example_folder, fname)}

def generate_filename(): return str(round(time.time(), 1)).replace(".", "")

def upload(f, model, ext = ".png"):
    folder = (model_folder if model else upload_folder)
    fname = generate_filename() + ext
    resource('s3').Object(bucket, folder + '/'+ fname).put(Body=f, ContentType='image/png')
    return fname

def load_img(url):
    url = requests.utils.unquote(url)
    response = requests.get(url)
    img = PIL.Image.open(io.BytesIO(response.content))
    return img

def array_to_img(a, format="PNG", cmap=cm.nipy_spectral):
    ## Normalize color map to data
    norm = colors.Normalize(vmin = a.min(), vmax=a.max())
    norm_color_map = cm.ScalarMappable(norm=norm, cmap=cmap)

    ## Convert image from array and save to buffer
    im = PIL.Image.fromarray(norm_color_map.to_rgba(a, bytes=True))
    buf = io.BytesIO()
    im.save(buf, format=format)
    buf.seek(0)
    return buf
