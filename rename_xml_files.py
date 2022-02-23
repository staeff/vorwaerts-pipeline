import csv
import shutil
from pathlib import Path


# Align xml filename with image file name
with open('datafolder/metadaten.csv') as csv_file:
    csv_reader = csv.reader(csv_file)
    # Skip the first line
    next(csv_reader)
    for row in csv_reader:
        name = Path(row[5])
        target = 'datafolder/xml' / name.with_suffix('.xml')
        source = Path(f'datafolder/xml/{row[6]}')
        # XXX Add logging here!
        shutil.move(source, target)
