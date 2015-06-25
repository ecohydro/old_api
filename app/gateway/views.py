from flask import make_response, request
from flask import current_app as app
from app import gateway_q
from .SMS import SMS
from app.make_error import make_error
from twilio.util import RequestValidator as validator

from . import gateway


def SMSjob(SMS):
    SMS.get()
    SMS.clean()
    SMS.post()


@gateway.route('/smssync', methods=['POST'])
def post_smssync():
    if request.headers['Content-Type'].lower() in app.config['FORM'].lower():
        data = {}
        try:
            for key in request.form:
                data[key] = request.form[key]
        except:
            return make_error(400, 'No message data provided')
        if 'message' not in data:
            return make_error(400, 'No message data provided')
        if 'secret' not in data and app.config['GATEWAY_SECRET']:
            return make_error(401, 'Message requires authentication: [secret]')
        if not str(data['secret']) == str(app.config['GATEWAY_SECRET']):
            return make_error(
                403,
                'Message failed authentication: [secret] is incorrect')
        if 'message_id' in data:
            message_id = data['message_id']
        else:
            from random import randint
            message_id = str([randint(0, 9) for x in range(31)])
        thisSMS = SMS.create(
            resource='smssync',
            message_id=message_id,
            data=data)
        gateway_q.enqueue(SMSjob, thisSMS)
    else:
        return make_error(400, message='POST requires FORM data')
    resp = make_response('{payload: {success:"true"}}', 200)
    resp.mimetype = 'application/json'
    return resp


@gateway.route('/twilio', methods=['POST'])
def post_twilio():
    if request.headers['Content-Type'].lower() in app.config['FORM'].lower():
        if request.form:
            if 'X-Twilio-Signature' in request.headers:
                try:
                    signature = request.headers['X-Twilio-Signature']
                    if app.config['TWILIO_POST_URL'] and \
                            app.config['TWILIO_AUTH_TOKEN']:
                        url = app.config['TWILIO_POST_URL']
                        auth = app.config['TWILIO_AUTH_TOKEN']
                    else:
                        return make_error(
                            500,
                            'app.config is missing Twilio Authentication')
                    # print request.form
                    # print signature
                    if validator(auth).validate(url, request.form, signature):
                            thisSMS = SMS.create(
                                message_id=request.form['MessageSid'],
                                resource='twilio')
                            gateway_q.enqueue(SMSjob, thisSMS)
                    else:
                        return make_error(
                            403,
                            'Twilio Message failed HMAC Authentication')
                except KeyError:
                    return make_error(
                        500,
                        'app.config is missing Twilio Authentication')
            else:
                return make_error(
                    401,
                    'Must provide X-Twilio-Signature header')
        else:
            return make_error(400, 'No form data provided')
    else:
        return make_error(400, 'POST requires FORM data')
    r = make_response('<Response></Response>', 202)
    r.mimetype = 'text/xml'
    return r
