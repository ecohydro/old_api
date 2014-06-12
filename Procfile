# web: gunicorn --access-logfile - --error-logfile - --log-level debug api:app
web: newrelic-admin run-program python manage.py serve
worker: python -u worker.py

