from utils import create_path
from PIL import Image
import multiprocessing as mp
import json


def crop_image(img_obj, features, outpath):
    """Extract the image by given coordinates

    feature is a dict.
    feature["coords"] is a tuple with 4 numerical
    values defining the position of the element on the
    page.
    """
    file_id = features["file_id"]
    block_id = features["block_id"]
    cropped = img_obj.crop(features["coords"])
    cropped.save(outpath / f"{file_id}-{block_id}.jpg")


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

    # Create a folder for every Newspaper page
    # e.g. /vw-1891-01-04-3-004/ to contain the subelements
    outpath = create_path(f"images/{file_id}/")

    # Turn original image into a PIL obj
    # XXX Do we have to do this each iteration?
    img_obj = Image.open(f"datafolder/images/{file_id}.jpg")
    crop_image(img_obj, features, outpath)

if __name__ == "__main__":

    with open("datafolder/json/advertisments.json", "r") as infile:
        data = json.load(infile)

    pool = mp.Pool(mp.cpu_count())
    pool.map(process_entry, [entry for entry in data])
    pool.close()
