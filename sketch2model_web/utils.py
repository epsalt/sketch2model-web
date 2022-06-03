import base64
import io
from PIL import Image
from matplotlib import cm, colors

from sketch2model_web import app

max_width = app.config["MAX_IMAGE_SIZE"]
max_height = app.config["MAX_IMAGE_SIZE"]
allowed_extensions = app.config["ALLOWED_EXTENSIONS"]


def resize(im):
    im = Image.open(im)
    resize_ratio = min(max_width / im.width, max_height / im.height, 1)
    new_width = round(resize_ratio * im.width)
    new_height = round(resize_ratio * im.height)
    im = im.resize((new_width, new_height), Image.ANTIALIAS)
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    return buf


def load_img(img):
    data = base64.b64decode(img)
    buf = io.BytesIO(data)
    img = Image.open(resize(buf))
    return img


def array_to_img(a, cmap, format="PNG"):
    # Normalize color map to data

    cmap_dict = {
        "viridis": cm.viridis,
        "inferno": cm.inferno,
        "plasma": cm.plasma,
        "magma": cm.magma,
        "Accent": cm.Accent,
        "Dark2": cm.Dark2,
        "Paired": cm.Paired,
        "Pastel1": cm.Pastel1,
        "Paste2": cm.Pastel2,
        "Set1": cm.Set1,
        "Set2": cm.Set2,
        "Set3": cm.Set3,
    }

    norm = colors.Normalize(vmin=a.min(), vmax=a.max())
    norm_color_map = cm.ScalarMappable(norm=norm, cmap=cmap_dict.get(cmap))

    # Convert image from array and save to buffer
    im = Image.fromarray(norm_color_map.to_rgba(a, bytes=True))
    buf = io.BytesIO()
    im.save(buf, format=format)
    buf.seek(0)
    return buf


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions
