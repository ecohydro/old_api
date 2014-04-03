web: gunicorn --access-logfile - --error-logfile - --log-level debug api:app
#web:  newrelic-admin run-program waitress-serve --port=$PORT --host=$HOST api:app
worker: python worker.py

