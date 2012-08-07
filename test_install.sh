#!/bin/sh

virtualenv2 /tmp/env || virtualenv /tmp/env
. /tmp/env/bin/activate
pip install .
