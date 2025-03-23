#!/bin/bash

# -----------------------------------------------------------------------------
#  Project: Essential Gadgets
#  Author: Thanh Dancer <congthanh@0x1115.com>
#  Created Date: 10/01/2025
#  Updated Date: 17/01/2025
#  Description: This script sets up a frontend local development server for 
#               the project.
# -----------------------------------------------------------------------------

# Set up the local development server
APPLICATION_PATH=${1:-"/app/web"}
cd $APPLICATION_PATH

# Install the dependencies
npm install

# Start the local development server
npm run dev