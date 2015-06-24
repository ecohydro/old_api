from flask import make_response, abort
from flask import current_app as app
from app import post_q
import json
from . import hirefire


@hirefire.route('/hirefire/<key>/info', methods=['GET'])
def hirefire_info(key):
    with app.app_context():
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


@hirefire.route('/hirefire/test', methods=['GET'])
def hirefire_test():
    resp = make_response("HireFire", 200)
    resp.mimetype = "text/html"
    return resp
