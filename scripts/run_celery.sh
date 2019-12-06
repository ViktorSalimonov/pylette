#!/bin/bash

cd app || exit
su -m app -c "celery -A app.celery worker --loglevel=info"
