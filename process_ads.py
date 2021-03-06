import io
import json
import multiprocessing as mp
import os
from distutils.util import strtobool

from dotenv import load_dotenv
from PIL import Image

from utils import create_path, get_s3_bucket

load_dotenv()
USE_AWS = strtobool(os.getenv("USE_AWS", "False"))
AWS_AD_IMAGES_BUCKET = os.getenv("AWS_AD_IMAGES_BUCKET")


def crop_image(img_obj, features):
    """Extract the image by given coordinates

    feature is a dict.
    feature["coords"] is a tuple with 4 numerical
    values defining the position of the element on the
    page.
    """
    file_id = features["file_id"]
    block_id = features["block_id"]
    image_name = f"{file_id}-{block_id}.jpg"
    image_path = f"output/images/ad_images/{image_name}"
    image_format = img_obj.format
    cropped = img_obj.crop(features["coords"])
    cropped.save(image_path, image_format)
    if USE_AWS:
        save_image_s3(cropped, image_name, image_format)


def save_image_s3(cropped, image_name, image_format):
    # XXX Move bucket out and cache it
    s3bucket = get_s3_bucket(AWS_AD_IMAGES_BUCKET)
    in_mem_img = io.BytesIO()
    cropped.save(in_mem_img, image_format)
    in_mem_img.seek(0)
    s3msg = s3bucket.put_object(
        Key=image_name, Body=in_mem_img, ContentType="image/jpeg"
    )
    print(s3msg)


def extract_id(block_id_string):
    """Gets something block id string like Page1_Block1
    and returns the remaining number when Page1_Block
    is removed.
    """
    return block_id_string.replace("Page1_Block", "")


def get_coordinates(fields):
    """Get coordinates of a block"""
    x0 = int(fields["x"])
    y0 = int(fields["y"])
    x1 = int(fields["width"]) + x0
    y1 = int(fields["height"]) + y0
    return (x0, y0, x1, y1)


def process_entry(entry):
    """Process a single entry to transform an image"""
    fields = entry["fields"]
    file_id = fields["file_id"]
    features = {
        "coords": get_coordinates(fields),
        "block_id": fields["block_id"],
        "file_id": file_id,
    }

    # Turn original image into a PIL obj
    img_obj = Image.open(f"datafolder/images/{file_id}.jpg")
    crop_image(img_obj, features)


if __name__ == "__main__":

    with open("output/json/advertisments.json", "r") as infile:
        data = json.load(infile)

    # Create folder for the images if needed
    create_path(f"output/images/ad_images")

    pool = mp.Pool(mp.cpu_count())
    pool.map(process_entry, [entry for entry in data])
    pool.close()
