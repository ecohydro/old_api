#!/usr/bin/python
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
    print('Starting coverage')

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, eve_mongo, pymongo, slack
from app.shared.models import db, g

# Import Models for MongoEngine
from app.shared.models.user import User
from app.shared.models.pod import Pod
from app.shared.models.data import Data
from app.shared.models.sensor import Sensor
from app.shared.models.notebook import Notebook
from app.shared.models.message import Message
from app.shared.models.message import NewMessageObject as NewMessage
from flask.ext.script import Manager, Shell

print('Using CONFIG ' + os.getenv('FLASK_CONFIG'))
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

from mqtt import mqttc


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
        NewMessage=NewMessage,
        slack=slack,
        mqttc=mqttc,
        g=g
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
def test(coverage=False):
    if app.testing:
        print "Starting Tests"
        if coverage and not os.environ.get('FLASK_COVERAGE'):
            import sys
            print "Reloading for coverage"
            os.environ['FLASK_COVERAGE'] = '1'
            print sys.argv
            os.execvp(sys.executable, [sys.executable] + sys.argv)
        """Run the tests (using nose)"""
        if COV:
            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()
            basedir = os.path.abspath(os.path.dirname(__file__))
            covdir = os.path.join(basedir, 'cover')
            COV.html_report(directory=covdir)
            print('HTML version: file://%s/index.html' % covdir)
            COV.erase()
        import nose
        nose.main(argv=[''])
    else:
        print "ERROR: Must use testing config"


@manager.command
def serve():
    from waitress import serve
    port = int(os.getenv('PORT', 5000))
    threads = int(os.getenv('WAITRESS_THREADS', 4))
    serve(app, port=port, threads=threads)

if __name__ == '__main__':
    manager.run()
