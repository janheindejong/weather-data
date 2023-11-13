#!/bin/sh 

set -e 

ruff check . 
black --check .
mypy .
pytest .

