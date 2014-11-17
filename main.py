import feedparser, shelve, wgetter, re, os, zipfile
from clint.textui import prompt, puts, colored, indent
from time import mktime
from datetime import datetime

db = shelve.open("shelve.db")

COMIC_DIR = "jl8-comics/"
DIST_DIR = "dist/"
if not os.path.exists(COMIC_DIR):
	os.makedirs(COMIC_DIR)
if not os.path.exists(DIST_DIR):
	os.makedirs(DIST_DIR)

debug=True

d = feedparser.parse('http://limbero.org/jl8/rss/')



tempfiles = [ f for f in os.listdir(COMIC_DIR) if f.endswith(".tmp") ]

for f in tempfiles:
	if debug:
		with indent(5, quote=">"):
			puts(colored.red("Deleting temp file:"+f))
	os.remove(COMIC_DIR+f)

skipped=0

for entry in d['entries']:
	if entry['title'].encode("utf-16le") not in db.keys():
		url = re.search('src="([^"]+)"',entry['summary_detail']['value']).group(1)
		entry_date = datetime.fromtimestamp((mktime(entry['published_parsed'])))
		puts(colored.white("Downloading comic: "+entry['title'].encode("utf-16le")))
		with indent(5, quote=">"):
			puts(colored.white("Published on:"+str(datetime.now()-entry_date)))

		filename = wgetter.download(url,outdir=COMIC_DIR)
		entry['title']=entry['title'].encode("utf-16le")
		db[entry['title']]=entry
	else:
		skipped=skipped+1
db.close()

comicfiles = [ f for f in os.listdir(COMIC_DIR)]

puts(colored.white("Creating CBZ file"))
zf = zipfile.ZipFile("dist/jl8-comics.cbz", "w")
for f in comicfiles:
	if f not in zf.namelist():
		puts(colored.yellow("Adding "+f+" to CBZ"))
		zf.write(COMIC_DIR+f,f)
zf.close()
puts(colored.white("Done!"))
