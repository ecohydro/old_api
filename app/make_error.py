from flask import jsonify


def make_error(status_code, message):
    response = jsonify({
        'status_code': status_code,
        'status': 'ERR',
        'error': message
    })
    response.status_code = status_code
    response.mimetype = 'application/json'
    return response
