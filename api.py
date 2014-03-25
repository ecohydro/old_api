import os
from eve import Eve
from utils import pod_name

# We've defined a ONHEROKU variable to determine if we are, well, on Heroku. 
if os.environ.get('ONHEROKU'):
	host = '0.0.0.0'
	port = int(os.environ.get('PORT'))
	debug = False # Don't debug on Heroku.
	settings = '/app/settings.py'
else:
	host = '0.0.0.0'
	port = 5000 
	debug = True
	settings = '../settings.py'

app = Eve(settings=settings)

def before_insert_pod(documents):
	for d in documents:
		print "Adding " + d["name"] + " to the database"

def before_insert_data(documents):
	print "A POST to data was just performed!"
	for d in documents:
		print "Posting " + d["s"] + " data from " + d["p"] + " to the database"

def before_insert_notebook(documents):
	for d in documents:
		print "Adding " + d["name"] + " notebook to the database"

# Heroku defines a $PORT environment variable that we use to determine

# Start the application
if __name__ == 'api':
# Adding data to the system:
	app.on_insert_data += before_insert_data
# Administering pods, gateways, and sensors:
# Run the program:
#	app.run(host=host, port=port, debug=debug)
