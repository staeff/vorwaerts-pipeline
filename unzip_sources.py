import zipfile

zip_file = "sourcedata/anzeigen.zip"
outpath = 'data'

with zipfile.ZipFile(zip_file) as zip:
    zip.extractall(outpath)
