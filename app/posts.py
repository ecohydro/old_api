from flask import current_app as app


def post_process_message(message=None):
    app.logger.info("Starting post process job")
    if message is None:
        app.logger.error("Must provide message")
    message.init()
    if message.status == 'queued':
        try:
            message.parse()
            message.post()
            message.save()
            message.slack()
        except:
            message.status = 'invalid'
            message.save()
            app.logger.warning('Bad message recieved by API')
