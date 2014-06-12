from flask import Blueprint

hirefire = Blueprint('hirefire', __name__, url_prefix='')

from . import views