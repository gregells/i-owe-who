# Original starting command
web: gunicorn --config gunicorn.conf.py i_owe_who.wsgi

# Updated command w/ proxy for static IP for database connection
# https://devcenter.heroku.com/articles/fixie-socks
# https://github.com/usefixie/fixie-wrench
# web: ./bin/fixie-wrench LOCAL_PORT:REMOTE_HOST:REMOTE_PORT & ...
# web: ./bin/fixie-wrench -v 1234:$DATABASE_BASE_URL:5432 & gunicorn --config gunicorn.conf.py i_owe_who.wsgi

# Uncomment this `release` process if you are using a database, so that Django's model
# migrations are run as part of app deployment, using Heroku's Release Phase feature:
# https://docs.djangoproject.com/en/5.2/topics/migrations/
# https://devcenter.heroku.com/articles/release-phase
# Without proxy:
release: ./manage.py migrate --no-input
# With proxy:
# release: ./bin/fixie-wrench -v 1234:$DATABASE_BASE_URL:5432 & ./manage.py migrate --no-input
