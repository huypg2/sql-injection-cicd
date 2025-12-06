#!/bin/bash
echo "Running unit tests..."
pytest ../detection_api/tests --disable-warnings -q
