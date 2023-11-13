#!/bin/sh 

set -e

rm -rf .venv 
rm -rf .ruff_cache .pytest_cache .mypy_cache .coverage .test-output

source ./scripts/reset_dev_db.sh
