#!/bin/bash

# -----------------------------------------------------------------------------
#  Project: Essential Gadgets
#  Script: 2_web_build.sh
#  Author: Thanh Dancer <congthanh@0x1115.com>
#  Created Date: 10/01/2025
#  Description: This script builds the project for production.
# -----------------------------------------------------------------------------

# Navigate to the project directory
APPLICATION_PATH=${1:-"/app/web"}
cd $APPLICATION_PATH

# Install dependencies
npm install

# Build the project
# This command will minify the code and optimize the assets for production
# Output will be stored in the `out` directory
npm run build

# Copy the built files to the deployment directory
# Base directories
WEB_OUT="/app/web/out"
WEB_SITES="/app/websites"

# Ensure the source directory exists
if [ ! -d "$WEB_OUT" ]; then
    echo "Source directory $WEB_OUT does not exist."
    exit 1
fi

# Ensure the target directory exists
if [ ! -d "$WEB_SITES" ]; then
    echo "Target directory $WEB_SITES does not exist."
    exit 1
fi

# Iterate over all subdirectories in /app/websites/
for site in "$WEB_SITES"/*; do
    # Check if it is a directory
    if [ -d "$site" ]; then
        echo "Processing site: $site"
        
        # Clean the site but keep the .git folder
        find "$site" -mindepth 1 \
            -not -path "$site/.git" \
            -not -path "$site/.git/*" \
            -not -path "$site/CNAME" \
            -not -path "$site/.nojekyll" \
            -delete
        
        # Copy files from /app/web/out to the site
        echo "Copying files to $site"
        cp -r "$WEB_OUT/"* "$site/"
    fi
done

echo "Operation completed successfully!"