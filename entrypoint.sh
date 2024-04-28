#!/bin/sh
git config --global --add safe.directory /github/workspace
git config --global user.email "ellen2imagine@gmail.com"
git config --global user.name "Ellen Xu"
. /venv/bin/activate
python -m main
