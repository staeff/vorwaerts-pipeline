from pathlib import Path
from PIL import Image
from lxml import etree
import os

NS = "{http://www.loc.gov/standards/alto/ns-v2#}"


def crop_image(img_obj, features, outpath):
    """Extract the image by given coordinates"""
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


def get_coordinates(item_attrs):
    """Get coordinates of a block"""
    x0 = int(item_attrs["HPOS"])
    y0 = int(item_attrs["VPOS"])
    x1 = int(item_attrs["WIDTH"]) + x0
    y1 = int(item_attrs["HEIGHT"]) + y0
    return (x0, y0, x1, y1)

def get_features(block):
    """Get attributes from block
        that are needed for further processing
    """
    item_attrs = block.attrib
    # Assign nodes attributes dict to a var
    features = {
        "coords": get_coordinates(item_attrs),
        "block_id": extract_id(item_attrs["ID"]),
        "file_id": file_id,
    }
    return features

def create_path(file_id):
    """Create a folder for every Page

        e.g. /vw-1891-01-04-3-004/
        To organize the images of ads, that each is
        split into.
    """
    cwd = Path.cwd()
    path = f"images/{file_id}/"
    dirname = cwd / path
    if not dirname.exists():
        os.makedirs(dirname, exist_ok=True)
    return dirname


def get_xmlfile_paths():
    """Return pathlib Paths of xml files processed."""
    cwd = Path.cwd()
    xml_files = sorted(list(cwd.glob("datafolder/xml/*.xml")))
    return xml_files


if __name__ == "__main__":

    xml_files = get_xmlfile_paths()

    for i, xml_file in enumerate(xml_files):
        file_id = xml_file.stem
        outpath = create_path(file_id)

        # Turn original image into a PIL obj
        # XXX Do we have to do this each iteration?
        img_obj = Image.open(f"datafolder/images/{file_id}.jpg")

        # parse XML file into etree
        tree = etree.parse(str(xml_file))

        # Extract all textblocks elements
        textblocks = tree.findall(f".//{NS}TextBlock")

        for block in textblocks:
            features = get_features(block)
            crop_image(img_obj, features, outpath)
