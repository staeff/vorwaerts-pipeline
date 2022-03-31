from PIL import Image
from pathlib import Path
from utils import create_path
from utils import get_s3_bucket
import io

scansize = (1320, 1320)
thumbsize = (400, 400)
cwd = Path(".")
images = cwd.glob("datafolder/images/*.jpg")


def process_image(image):
    """Create smaller version and thumbnail of original scan"""
    with Image.open(image) as im:

        print(f"processing file {image.name}")

        im.thumbnail(scansize)
        im.save(output_img_path / "scans" / image.name, im.format)
        in_mem_scan = io.BytesIO()
        im.save(in_mem_scan, im.format)
        in_mem_scan.seek(0)
        s3msg = s3bucket.put_object(
            Key=f"scans/{image.name}", Body=in_mem_scan, ContentType="image/jpeg"
        )
        print(s3msg)

        im.thumbnail(thumbsize)
        im.save(output_img_path / "thumbnails" / image.name, im.format)
        in_mem_thumb = io.BytesIO()
        im.save(in_mem_thumb, im.format)
        in_mem_thumb.seek(0)
        s3msg = s3bucket.put_object(
            Key=f"thumbnails/{image.name}", Body=in_mem_thumb, ContentType="image/jpeg"
        )
        print(s3msg)

if __name__ == '__main__':
    output_img_path = create_path("output/images")
    create_path("output/images/scans")
    create_path("output/images/thumbnails")
    s3bucket = get_s3_bucket("vorwaerts-images")

    for image in images:
        process_image(image)
