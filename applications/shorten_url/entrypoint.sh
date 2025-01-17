#!/bin/bash

# Navigate to the directory containing the Flask application
cd /app/shorten_url


# Install the required packages for the Flask application
pip install -r requirements.txt

# Symbolic link shared library
ln -s /app/internal /app/shorten_url/internal

# Run the Flask application
flask run --host=0.0.0.0 --port 8080 --debug 