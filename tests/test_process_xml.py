from lxml import etree
from process_xml import generate_model_dict
from process_xml import generate_page_fields
from process_xml import get_page_dimensions
from process_xml import get_adv_coords
from process_xml import get_adv_text
from process_xml import extract_id
from process_xml import NS

XML_PAGE_COORDS = """
<alto xmlns="http://www.loc.gov/standards/alto/ns-v2#">
  <Page ID="Page1" PHYSICAL_IMG_NR="1" HEIGHT="5132" WIDTH="3504"/>
</alto>
"""

XML_TextLine_CONTENT = """
<alto xmlns="http://www.loc.gov/standards/alto/ns-v2#">
  <TextLine>
    <String CONTENT="Andreas," WC="0.75" />
    <String
      CONTENT="Alexander"
      SUBS_TYPE="HypPart1"
      SUBS_CONTENT="Alexanderstraße"
      WC="0.50" />
  </TextLine>
  <TextLine>
    <String
      CONTENT="straße"
      SUBS_TYPE="HypPart2"
      SUBS_CONTENT="Alexanderstraße"
      WC="0.60" />
  </TextLine>
</alto>
"""

def test_generate_model_dict():
    i = 10
    model = 'app.model'

    result = generate_model_dict(i, model)

    assert len(result) == 2
    assert result['pk'] == 10
    assert result['model'] == "app.model"

def test_generate_page_fields():
    file_id_string = 'vw-1891-12-20-298-012'

    fields = generate_page_fields(file_id_string)

    assert len(fields) == 4
    assert fields['file_id'] == "vw-1891-12-20-298-012"
    assert fields["publish_date"] == "1891-12-20"
    assert fields["issue_number"] == 298
    assert fields["page_number"] == 12

def test_get_page_dimensions():
    tree = etree.fromstring(XML_PAGE_COORDS)

    result = get_page_dimensions(tree, NS)
    assert len(result) == 2
    assert result['height'] == "5132"
    assert result['width'] == "3504"

def test_get_adv_text():
    tree = etree.fromstring(XML_TextLine_CONTENT)

    result = get_adv_text(tree, NS)
    assert result == 'Andreas, Alexanderstraße'

def test_get_adv_coords():
    item_attrs = dict(HPOS='100',VPOS='200',WIDTH='22',HEIGHT='12')

    result = get_adv_coords(item_attrs)

    assert len(result) == 4
    assert result['x'] == 100
    assert result['y'] == 200
    assert result['width'] == 22
    assert result['height'] == 12

def test_extract_id():
    block_id_string = 'Page1_Block25'

    result = extract_id(block_id_string)

    assert result == '25'
