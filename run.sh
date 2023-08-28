#!/bin/sh

gunicorn -w 4 "app:app" -b 0.0.0.0:5000 -t 0
# flask --app app run --debug --host=0.0.0.0 --port=5000 
