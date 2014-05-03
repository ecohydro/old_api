import requests, sys
import time
import json
import urllib

import bitly_api
import qrcode
import qrcode.image.svg
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from flask import current_app as app
from sms import SMS

def post_data_to_API(objId,res):
	# Setup the URLs:
	url = app.config['API_URL'] + '/messages/' + res + '/' + objId
	message = SMS.create(url=url)
	# Init dicts for message updates and RQ responses:
	response={}
	
	if message.status == 'queued':
		message.parse()
		message.post()
		response = message.patch()
				
	return response

def post_pod_create_qr(objId):
	# First we need to get the pod
	url = app.config['API_URL'] + '/pods/' + objId
	pod = requests.get(url).json()

	# Set up the file names
	tmp_file = 'tmp.svg'
	pod_qr_file = str(pod['name']) + '.svg'
	
	try:
		bitly_url = app.config['APP_URL'] + '/pods/' + urllib.quote_plus(str(pod['name']))
		# Now we can generate the bitly url:
		c = bitly_api.Connection(access_token=app.config['BITLY_API_TOKEN'])
		bitly_link=c.shorten(url)['url']
		
		# Update the link title to this pod name:
		c.user_link_edit(bitly_link,'title',str(pod['name']))
		# Add this link to the PulsePod bundle:
		a = c.bundle_bundles_by_user()['bundles']
		bundle_link = a[next(index for (index, d) in enumerate(a) if d["title"] == "PulsePods")]['bundle_link']
		c.bundle_link_add(bundle_link,bitly_link)
	except:
		return "Error creating Bitly link"

	try:
		# Make the QR Code:
		img = qrcode.make(bitly_link,image_factory=qrcode.image.svg.SvgPathImage)
		f = open(tmp_file,'w')
		img.save(f)
		f.close()
	except:
		return "Error in making QR code file"

	try:
		# UPLOAD THE QRFILE TO S3:
		conn = S3Connection(app.config['AWS_ACCESS_KEY_ID'],app.config['AWS_SECRET_ACCESS_KEY'])
		bucket = conn.get_bucket('pulsepodqrsvgs')
		k = Key(bucket)
		k.key = pod_qr_file
		k.set_contents_from_filename(tmp_file)
		bucket.set_acl('public-read', pod_qr_file)
	except:
		return "Error writing file to Amazon S3"

	return "QR file successfully created"

