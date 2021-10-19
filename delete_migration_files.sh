#!/bin/bash

find ./delab -path "migrations/*.py" -not -name "__init__.py" -delete
find ./delab -path "migrations/*.pyc" -delete

find ./blog -path "migrations/*.py" -not -name "__init__.py" -delete
find ./blog -path "migrations/*.pyc" -delete

find ./users -path "migrations/*.py" -not -name "__init__.py" -delete
find ./users -path "migrations/*.pyc" -delete