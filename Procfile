#NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program 
web:  newrelic-admin run-program waitress-serve --port=$PORT --host=$HOST api:app
#web: newrelic-admin run-program gunicorn --access-logfile - --error-logfile - --log-level debug api:app
worker: python worker.py

