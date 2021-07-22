import os
import sys
import datetime
import json

today = datetime.datetime.today().strftime('%Y%m%d')
from christies.settings import outdir
# outdir = "."
outdir = "%s/%s/" %(outdir,today)


def writeToFile(spider_name, filename, content, mode = 'w' ):
    full_path = os.path.join(outdir, spider_name, filename)
    base_path = os.path.dirname(full_path)

    if not os.path.exists(base_path): os.makedirs(base_path)

    if mode == "wb":
        with open(full_path, mode) as f:
            f.write(content)
    else:
        with open(full_path, mode, encoding='utf8') as f:
            f.write(content)
    return