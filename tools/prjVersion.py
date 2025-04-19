# GITHUB_REF_NAME=v0.0.0
# os.environ.get('GITHUB_REF_NAME')

import os
import sys
import re
from pathlib import Path

rst = sys.argv[1]
version = sys.argv[2]
directory = sys.argv[3]

if not (re.match(r"^v[0-9]+[.][0-9]+[.][0-9]+", version)):
    print("Invalid version record format")
    exit(1);

files = Path(directory).glob("*.kicad_*")
for filename in files:
    tmpPath=os.path.join(filename)
    with open(tmpPath, "r") as f:
        print(f"Content of '{filename}'")
        filedata = f.read()
    if rst == 'S':
        filedata = filedata.replace('vV.V.V-VVV', version)
    else:
        filedata = filedata.replace(version, 'vV.V.V-VVV')
    with open(tmpPath, 'w') as f:
        f.write(filedata)
