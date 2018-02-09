#!/usr/bin/env bash

export VENV=venv-xqa-db-amqp
python3 -m venv $VENV
source $VENV/bin/activate
pip install --upgrade pip setuptools
pip install -r requirements.txt
deactivate
