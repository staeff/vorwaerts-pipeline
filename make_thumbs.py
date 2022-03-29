from PIL import Image
from pathlib import Path
from utils import create_path

scansize = (1320, 1320)
thumbsize = (400, 400)
cwd = Path(".")
images = cwd.glob("datafolder/images/*.jpg")
output_img_path = Path('images')

def process_image(image):
    """Create smaller version and thumbnail of original scan"""
    with Image.open(image) as im:
        print(f"processing file {image.name} done...")
        im.thumbnail(scansize)
        im.save(output_img_path / "scans" / image.name, im.format)
        im.thumbnail(scansize)
        im.save(output_img_path / "thumbnails" / image.name, im.format)

create_path('images/scans')
create_path('images/thumbnails')

for image in images:
    process_image(image)
