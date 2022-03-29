from PIL import Image
from pathlib import Path
#from utils import create_path
from utils import get_s3_bucket
import io

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
        in_mem_scan = io.BytesIO()
        #im.save(output_img_path / "scans" / image.name, im.format)
        im.save(in_mem_scan, im.format)
        in_mem_scan.seek(0)
        s3bucket.put_object(Key=f"scans/{image.name}", Body=in_mem_scan)

        im.thumbnail(thumbsize)
        in_mem_thumb = io.BytesIO()
        #im.save(output_img_path / "thumbnails" / image.name, im.format)
        im.save(in_mem_thumb, im.format)
        in_mem_scan.seek(0)
        s3bucket.put_object(Key=f"thumbnails/{image.name}", Body=in_mem_thumb)

#create_path('images/scans')
#create_path('images/thumbnails')
s3bucket = get_s3_bucket('vorwaerts-images')

for image in images:
    process_image(image)
