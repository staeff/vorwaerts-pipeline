from shutil import make_archive
from zipfile import ZipFile

file = "ouput"  # zip file name
directory = "output"
make_archive(file, "zip", directory)  # zipping the directory
print("Contents of the zip file:")
with ZipFile(f"{file}.zip", 'r') as zip:
   zip.printdir()
