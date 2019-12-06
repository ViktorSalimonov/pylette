#!/bin/bash

cd app || exit
su -m app -c "python app.py"
