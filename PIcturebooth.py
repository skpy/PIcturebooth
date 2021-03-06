# PIcture Booth
import fnmatch, glob, json, os, sys, time
import Image
import picamera
from flask import Flask, request, redirect, url_for, render_template, send_file

today = time.strftime("%Y%m%d")
path = 'photos/'+today+'/'

app = Flask(__name__)

# createa a thumbnail. pass just the file name, not its path
def create_thumbnail(photo):
	size = 800, 600
	outfile = os.path.splitext(photo)[0] + "_t.jpg"
	im = Image.open(path+photo)
	im.thumbnail(size)
	im.save(path+outfile, "JPEG")
	return outfile

# return a list of all thumbnails
def get_thumbnails(offset):
	thumbs = []
	for file in sorted(os.listdir(path)):
		if fnmatch.fnmatch(file, '*_t.jpg'):
			thumbs.append(file)
	if offset:
		return thumbs[offset+1:]
	else:
		return thumbs

# by default, show the gallery of this session's photos
@app.route('/')
@app.route('/gallery')
def gallery():
	return render_template('gallery.html', photopath=path)

@app.route('/photos/<path:photo>')
def show_photo(photo=None):
	return send_file('photos/'+photo)

@app.route('/refresh')
@app.route('/refresh/<int:offset>')
def refresh(offset=0):
	thumbs = get_thumbnails(offset)
	# return some JSON
	j = []
	for file in thumbs:
		d = {}
		d['url'] = file
		j.append(d)
	return json.dumps(j)

# control the camera from here
@app.route('/camera', methods=['GET', 'POST'])
def camera():
	if request.method == 'POST':
		now = time.strftime("%H%M%S")
		with picamera.PiCamera() as camera:
			photo=path+now+'.jpg'
			camera.resolution = (2592, 1944)
			camera.vflip = True
			camera.capture(photo)
			thumb = create_thumbnail( os.path.basename(photo) )
			thumbnail = '<img src="'+path+thumb+'" />'
	elif request.method == 'GET':
		pictures = glob.glob(path+'*_t.jpg')
		if pictures:
			newest = max(pictures, key=os.path.getctime)
			thumbnail = '<img src="'+newest+'" />'
		else:
			# no images yet.
			thumbnail = 'Take a picture!'
	return render_template('camera.html', photo=thumbnail)

if __name__ == '__main__':
	# make sure a directory for today's photos exists
	if not (os.path.isdir(path)):
		os.mkdir(path)
	app.debug = True
	app.run(host='0.0.0.0')
