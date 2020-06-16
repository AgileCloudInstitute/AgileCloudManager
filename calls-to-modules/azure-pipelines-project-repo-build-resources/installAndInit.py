print("Inside Python script!")

import os
from pathlib import Path
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import zipfile

pathVar= os.environ['APPDATA'] +"\\terraform.d\plugins\windows_amd64\\"
print("pathVar is: " + pathVar)
Path(pathVar).mkdir(parents=True, exist_ok=True)

url = "https://github.com/microsoft/terraform-provider-azuredevops/releases/download/v0.1.2/terraform-provider-azuredevops_windows_amd64.zip"

file_name = url.split('/')[-1]
u = urllib2.urlopen(url)
f = open(file_name, 'wb')
file_size = int(u.getheader('Content-Length'))
print("Downloading: %s Bytes: %s" % (file_name, file_size))

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print(status)

f.close()

with zipfile.ZipFile(file_name, 'r') as zip_ref:
    zip_ref.extractall(pathVar)

os.remove(file_name)
