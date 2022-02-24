import zipfile

zip_file = "sourcedata/anzeigen.zip"
outpath = 'datafolder'

with zipfile.ZipFile(zip_file) as zip:
    zip.extractall(outpath)
