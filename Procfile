# web: gunicorn api:app --access-logfile - --error-logfile - --log-level debug  --worker-class gevent
web: newrelic-admin run-program python -u manage.py serve
worker: python -u worker.py

