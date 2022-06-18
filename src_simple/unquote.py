import urllib.parse
import sys

datafile = sys.argv[1]
with open(datafile) as f:
    lines = f.readlines()
    for line in lines:
        print(urllib.parse.unquote_plus(line))
f.close()

