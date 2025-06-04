@echo off

IF "%1" == "build" (
  echo "Building executable..."
  poetry run pyinstaller pilotng.spec
) ELSE (
  poetry run python main.py
)
