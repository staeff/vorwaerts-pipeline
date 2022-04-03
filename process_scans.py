from PIL import Image
from pathlib import Path
from utils import create_path
from utils import get_s3_bucket
import io
from dotenv import load_dotenv
from distutils.util import strtobool
import os

load_dotenv()
USE_AWS = strtobool(os.getenv("USE_AWS", "False"))
AWS_IMAGES_BUCKET = os.getenv("AWS_IMAGES_BUCKET")


scansize = (1320, 1320)
thumbsize = (400, 400)
cwd = Path(".")
images = cwd.glob("datafolder/images/*.jpg")


def save_image_s3(cropped, image_name, image_format):
    in_mem_img = io.BytesIO()
    cropped.save(in_mem_img, image_format)
    in_mem_img.seek(0)
    s3msg = s3bucket.put_object(
        Key=image_name, Body=in_mem_img, ContentType="image/jpeg"
    )
    print(s3msg)


def process_image(image):
    """Create smaller version and thumbnail of original scan"""
    with Image.open(image) as im:

        print(f"processing file {image.name}")
        scan_path = f"scans/{image.name}"
        thumb_path = f"thumbnails/{image.name}"
        image_format = im.format

        im.thumbnail(scansize)
        im.save(output_img_path / scan_path, image_format)
        if USE_AWS:
            save_image_s3(im, scan_path, image_format)

        im.thumbnail(thumbsize)
        im.save(output_img_path / thumb_path, im.format)
        if USE_AWS:
            save_image_s3(im, thumb_path, image_format)


if __name__ == "__main__":
    output_img_path = create_path("output/images")
    create_path("output/images/scans")
    create_path("output/images/thumbnails")
    if USE_AWS:
        s3bucket = get_s3_bucket(AWS_IMAGES_BUCKET)

    for image in images:
        process_image(image)
