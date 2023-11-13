#!/bin/sh 

set -e

black .
ruff check . --fix
