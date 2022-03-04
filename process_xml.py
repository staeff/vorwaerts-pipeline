from pathlib import Path
from lxml import etree
import json

NS = "{http://www.loc.gov/standards/alto/ns-v2#}"

def generate_model_dict(i, model):
    """Generate a dictionary with that represents a minimal page instance"""
    return dict(model=model, pk=i)

def generate_page_fields(file_id_string):
    _, year, month, day, issue_number, page_number = file_id_string.split("-")
    fields = {
        "file_id": file_id_string,
        "publish_date": f"{year}-{month}-{day}",
        "issue_number": int(issue_number),
        "page_number": int(page_number)
    }
    return fields

def get_page_coords(tree, NS):
    page_elem = tree.find(f".//{NS}Page")
    coords = {
        'height': page_elem.attrib['HEIGHT'],
        'width': page_elem.attrib['WIDTH']
    }
    return coords

def get_adv_coords(item_attrs):
    """Gets a block node, either TextBlock
    or Illustration and returns a
    dictionary with its attributes
    """
    adv_coords = {
        "x": int(item_attrs["HPOS"]),
        "y": int(item_attrs["VPOS"]),
        "width": int(item_attrs["WIDTH"]),
        "height": int(item_attrs["HEIGHT"])
    }
    return adv_coords

def get_adv_text(xml_node, NS):
    """copied from alto-tools

    https://github.com/cneud/alto-tools
    """
    text = ''

    # Use XPath here to simplify?
    for lines in xml_node.findall(f'.//{NS}TextLine'):
        for line in lines.findall(f'.//{NS}String'):
            # Check if there are no hyphenated words
            # We dont want to have the CONTENT of nodes, that have the
            # Attributes SUBS_CONTENT of SUBS_TYPE
            if ('SUBS_CONTENT' not in line.attrib and 'SUBS_TYPE' not in line.attrib):
                text += f"{line.attrib.get('CONTENT')} "
            else:
                # If a node has the Attribut SUBS_TYPE we check if
                # it is HypPart1 and add its SUBCONTENT_VALUE to text/
                if ('HypPart1' in line.attrib.get('SUBS_TYPE')):
                    text += f"{line.attrib.get('SUBS_CONTENT')} "
                    # This doesnt do shit!
                    if ('HypPart2' in line.attrib.get('SUBS_TYPE')):
                        pass
    return text.strip()

def extract_id(block_id_string):
    """Gets something block id string like Page1_Block1
    and returns the remaining number when Page1_Block
    is removed.
    """
    return block_id_string.replace("Page1_Block", "")


if __name__ == "__main__":
    cwd = Path(".")
    xml_files = sorted(list(cwd.glob("xml/*.xml")))
    fixture = []
    anzeigen = []
    j = 0

    for i, xml_file in enumerate(xml_files, 1):
        # parse XML file into etree
        tree = etree.parse(str(xml_file))

        # id string is filename w/o extensions
        file_id_string = xml_file.stem

        # Generate dict with page
        page_dict = generate_model_dict(i, 'vorwaerts.newspaperpage')
        fields_dict = generate_page_fields(file_id_string)
        coords_dict = get_page_coords(tree, NS)
        # Merge fields and coords dict
        fields = {**fields_dict, **coords_dict}
        page_dict['fields'] = fields
        fixture.append(page_dict)

        # Extract all textblocks elements
        textblocks = tree.findall(f".//{NS}TextBlock")

        for block in textblocks:
            # Assign nodes attributes dict to a var
            item_attrs = block.attrib
            j += 1
            ad_dict = generate_model_dict(j, 'vorwaerts.classifiedad')
            block_id_string = item_attrs["ID"]
            ad_fields = get_adv_coords(item_attrs)
            ad_fields["block_id"] = extract_id(block_id_string)
            ad_fields["file_id"] = file_id_string
            ad_fields["text"] = get_adv_text(block, NS)
            ad_fields["newspaper_page"] = i
            ad_dict['fields'] = ad_fields
            anzeigen.append(ad_dict)

    # Write pages data to fixture file
    with open("pages.json", "w") as outfile:
        json.dump(fixture, outfile)

    # Write advertisement data fo fixture
    with open("advertisments.json", "w") as outfile:
        json.dump(anzeigen, outfile)
