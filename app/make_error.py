from flask import jsonify


def make_error(status_code, message):
    """
    Generates an API error response from a status code and message

    Returns a response object that the API server can send to the client

    :param status_code: HTML status code for this error
    :param message: Error message from API

    """
    response = jsonify({
        'status_code': status_code,
        'status': 'ERR',
        'error': message
    })
    response.status_code = status_code
    response.mimetype = 'application/json'
    return response
