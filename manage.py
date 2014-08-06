#!/usr/bin/python
import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db, eve_mongo, pymongo

# Import Models for MongoEngine
from app.models.user import User
from app.models.pod import Pod
from app.models.data import Data
from app.models.sensor import Sensor
from app.models.notebook import Notebook
from app.models.message import Message
from app.models.message import NewMessageObject as NewMessage
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        pymongo=pymongo,
        Data=Data,
        Pod=Pod,
        User=User,
        Sensor=Sensor,
        Notebook=Notebook,
        Message=Message,
        client=app.test_client(),
        eve_mongo=eve_mongo,
        NewMessage=NewMessage
    )

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def reset():
    """Reset the testing database"""
    if app.testing:
        print "Reseting testing database"
        print "\t...dropping old collections"
        User.drop_collection()
        Pod.drop_collection()
        Notebook.drop_collection()
        Data.drop_collection()
        Sensor.drop_collection()
        Message.drop_collection()
        print "\t...generating new fake data"
        Sensor.generate_fake(15)
        User.generate_fake(10)
        Pod.generate_fake(20)
        Notebook.generate_fake(40)
        Data.generate_fake(300)
        Message.generate_fake(100)
    else:
        print "Cannot run this command under %s config" % \
            app.config['FLASK_CONFIG']


@manager.command
def test():
    """Run the tests (using nose)"""
    import nose
    nose.main(argv=[''])


@manager.command
def serve():
    from waitress import serve
    port = int(os.getenv('PORT', 5000))
    serve(app, port=port)

if __name__ == '__main__':
    manager.run()
