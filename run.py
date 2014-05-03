# Run a test server.
from app import app
from waitress import serve
import os

serve(app,port=os.getenv('PORT',8080))
#app.run(debug=True)
