import os
import shutil
import zipfile
from urllib.request import urlretrieve

url = "https://github.com/vaastav/Fantasy-Premier-League/archive/master.zip"

cwd = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(cwd, "data")
data_zip = os.path.join(cwd, "data.zip")

# remove existing data, if it exists
if os.path.exists(data_dir):
    shutil.rmtree(data_dir)

# remove existing zip file, if it exists
if os.path.isfile(data_zip):
    os.remove(data_zip)

# download the zip file and extract
filename, headers = urlretrieve(url, filename=data_zip)
with zipfile.ZipFile(data_zip, "r") as zip_ref:
    for d in zip_ref.namelist():
        p = d.split("/")
        # only extract the relevant data files
        if p[1].startswith("data"):
            zip_ref.extract(d, cwd)
            shutil.move(d, os.path.join(data_dir, "/".join(d.split("/")[2:])))

# remove the zip file
os.remove(data_zip)

# remove the temporary directory
shutil.rmtree(os.path.join(cwd, "Fantasy-Premier-League-master"))
