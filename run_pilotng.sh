#!/bin/bash

if [ "$1" == "build" ]; then
  echo "Building executable..."
  poetry run pyinstaller pilotng.spec
else
  poetry run python main.py
fi
