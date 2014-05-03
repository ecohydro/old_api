import os
from app import app
from waitress import serve

serve(app,port=os.getenv('PORT'))