import piexif
from PIL import Image
from io import BytesIO

def normalize_image_orientation(img_file):
    """Reads orientation tag from the exif data attached to a JPEG
    image. Returns the image rotated to normal orientation and with
    corresponding normal exif orientation tag.

    Note: horizontal (normal) exif value = 1
    """

    ### Open image and read orientation tag
    im = Image.open(img_file)
    exif_dict = piexif.load(im.info["exif"])
    orientation = exif_dict["0th"][piexif.ImageIFD.Orientation]
    print(orientation)

    ## Rotate image
    im = rotate_image_to_normal(im, orientation)

    ## Create new exif dict with base orientation value of 1
    exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
    exif_bytes = piexif.dump(exif_dict)

    ## Return file in a buffer
    buf = BytesIO()
    im.save(buf, "jpeg", exif=exif_bytes)
    buf.seek(0)
    return(buf)

def rotate_image_to_normal(im, orientation):
    """Rotates an image to normal horizontal orientation.

    Code modified from Rémy Hubscher's answer on stackoverflow 
    (http://stackoverflow.com/a/1608846)

    For reference: exif orientationd dict

    {1: 'Horizontal (normal)',
    2: 'Mirrored horizontal',
    3: 'Rotated 180',
    4: 'Mirrored vertical',
    5: 'Mirrored horizontal then rotated 90 CCW',
    6: 'Rotated 90 CW',
    7: 'Mirrored horizontal then rotated 90 CW',
    8: 'Rotated 90 CCW'}
    """

    if orientation == 1: return(im)
    elif orientation == 2: return(im.transpose(Image.FLIP_LEFT_RIGHT))
    elif orientation == 3: return(im.transpose(Image.ROTATE_180))
    elif orientation == 4: return(im.transpose(Image.FLIP_TOP_BOTTOM))
    elif orientation == 5: return(im.transpose(Image.FLIP_TOP_BOTTOM).transpose(IMAGE.ROTATE_90))
    elif orientation == 6: return(im.transpose(Image.ROTATE_270))
    elif orientation == 7: return(im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.Rotate_270))
    elif orientation == 8: return(im.transpose(Image.ROTATE_90))
