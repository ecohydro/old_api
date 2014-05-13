from flask import Blueprint, make_response, abort
from flask import current_app as app
from app import post_q
import json

hirefire_bp = Blueprint('hirefire_bp', __name__, url_prefix='')


@hirefire_bp.route('/hirefire/<key>/info', methods=['GET'])
def hirefire_info(key):
    if key == app.config['HIREFIRE_TOKEN']:
        resp = make_response(
            json.dumps([{
                'name': 'worker',
                'quantity': len(post_q.jobs)}]),
            200)
        resp.mimetype = 'application/json'
        return resp
    else:
        return abort(404)


@hirefire_bp.route('/hirefire/test', methods=['GET'])
def hirefire_test():
    resp = make_response("HireFire", 200)
    resp.mimetype = "text/html"
    return resp
