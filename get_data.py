import os
import shutil
import zipfile
import urllib.request

url = "https://github.com/vaastav/Fantasy-Premier-League/archive/master.zip"
fnm = "./data.zip"

filename, headers = urllib.request.urlretrieve(url, filename=fnm)
with zipfile.ZipFile(fnm, 'r') as zip_ref:
    zip_ref.extractall("./")

shutil.move("./Fantasy-Premier-League-master/data", "./data")
shutil.rmtree("./Fantasy-Premier-League-master")
os.remove("./data.zip")