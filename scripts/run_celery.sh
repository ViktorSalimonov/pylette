#!/bin/bash

cd app
su -m app -c "celery -A app.celery worker --loglevel=info"