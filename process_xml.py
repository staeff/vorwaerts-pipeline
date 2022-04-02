from utils import create_path
from utils import get_s3_bucket
from pathlib import Path
from dotenv import load_dotenv
from lxml import etree
import json
import os

NS = "{http://www.loc.gov/standards/alto/ns-v2#}"

load_dotenv()
AWS_DATA_BUCKET = os.getenv("AWS_DATA_BUCKET")


def generate_model_dict(i, model):
    """Generate a dictionary with that represents a minimal page instance"""
    return dict(model=model, pk=i)


def generate_page_fields(file_id_string):
    """Generate the fields attribute for a page"""
    _, year, month, day, issue_number, page_number = file_id_string.split("-")
    fields = {
        "file_id": file_id_string,
        "publish_date": f"{year}-{month}-{day}",
        "issue_number": int(issue_number),
        "page_number": int(page_number),
    }
    return fields


def get_page_dimensions(tree, NS):
    """Get the height and width of a complete page."""
    page_elem = tree.find(f".//{NS}Page")
    dimensions = {
        "height": page_elem.attrib["HEIGHT"],
        "width": page_elem.attrib["WIDTH"],
    }
    return dimensions


def get_adv_coords(item_attrs):
    """Gets a block node, either TextBlock
    or Illustration and returns a
    dictionary with its attributes
    """
    adv_coords = {
        "x": int(item_attrs["HPOS"]),
        "y": int(item_attrs["VPOS"]),
        "width": int(item_attrs["WIDTH"]),
        "height": int(item_attrs["HEIGHT"]),
    }
    return adv_coords


def get_word(entry):
    """Get the word contents of a String entry"""
    # Check whether we have a hyphenated word. The full word
    # is stored in SUBS_CONTENT
    text = ""
    if "SUBS_TYPE" in entry.attrib and "HypPart1" in entry.attrib.get("SUBS_TYPE"):
        text = f"{entry.attrib.get('SUBS_CONTENT')} "
    if "SUBS_CONTENT" not in entry.attrib and "SUBS_TYPE" not in entry.attrib:
        text = f"{entry.attrib.get('CONTENT')} "
    return text


def get_word_confidence(entry):
    """Get the value of the attribute WC as float

    Wc - word confidence. Value assigned by Abby OCR
    measuring the quality of the recognition.
    """
    return float(entry.attrib.get("WC"))


def get_line_attributes(xml_node, NS):
    """Get the text of an advertisement"""
    words = ""
    ocr_confidence = 0

    string_entries = xml_node.findall(f".//{NS}TextLine/{NS}String")
    for entry in string_entries:
        words += get_word(entry)
        ocr_confidence += get_word_confidence(entry)

    ocr_confidence = ocr_confidence / len(string_entries)

    line_attributes = {"text": words.strip(), "ocr_confidence": ocr_confidence}
    return line_attributes


def extract_id(block_id_string):
    """Gets something block id string like Page1_Block1
    and returns the remaining number when Page1_Block
    is removed.
    """
    return block_id_string.replace("Page1_Block", "")


if __name__ == "__main__":
    cwd = Path(".")
    xml_files = sorted(list(cwd.glob("datafolder/xml/*.xml")))
    fixture = []
    anzeigen = []
    # counter to have a numerical ID for each ad.
    ad_id = 0

    for i, xml_file in enumerate(xml_files, 1):
        # parse XML file into etree
        tree = etree.parse(str(xml_file))

        # id string is filename w/o extensions
        file_id_string = xml_file.stem

        # Generate dict with page
        page_dict = generate_model_dict(i, "vorwaerts.newspaperpage")
        fields_dict = generate_page_fields(file_id_string)
        coords_dict = get_page_dimensions(tree, NS)
        # Merge fields and coords dict
        fields = {**fields_dict, **coords_dict}
        page_dict["fields"] = fields
        fixture.append(page_dict)

        textblocks = tree.findall(f".//{NS}TextBlock")

        # A block constitutes one ad
        for block in textblocks:
            # Increment numerical ID for an ad
            ad_id += 1
            ad_dict = generate_model_dict(ad_id, "vorwaerts.classifiedad")
            # Assign nodes attributes dict to a var
            item_attrs = block.attrib

            block_id_string = item_attrs["ID"]
            # Get attributes text and ocr cofidence for an ad
            line_attributes = get_line_attributes(block, NS)
            ad_fields = get_adv_coords(item_attrs)
            ad_fields["block_id"] = extract_id(block_id_string)
            ad_fields["file_id"] = file_id_string
            ad_fields["text"] = line_attributes["text"]
            ad_fields["ocr_confidence"] = line_attributes["ocr_confidence"]
            ad_fields["newspaper_page"] = i
            ad_dict["fields"] = ad_fields
            anzeigen.append(ad_dict)

    # Store data on s3 for the web app to pick it up
    s3bucket = get_s3_bucket(AWS_DATA_BUCKET)
    s3bucket.put_object(Key="vorwaerts_ads_data.json", Body=json.dumps(anzeigen))
    s3bucket.put_object(Key="vorwaerts_pages_data.json", Body=json.dumps(fixture))

    # store data locally
    outpath = create_path("output/json")
    with open(f"{outpath}/pages.json", "w") as outfile:
        json.dump(fixture, outfile)

    with open(f"{outpath}/advertisments.json", "w") as outfile:
        json.dump(anzeigen, outfile)
