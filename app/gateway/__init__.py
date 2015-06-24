from flask import Blueprint

gateway = Blueprint('gateway', __name__, url_prefix='')

from . import views
