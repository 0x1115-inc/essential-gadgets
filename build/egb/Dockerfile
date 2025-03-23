# Essential Gadget Bootstrap
# Use an official Python runtime as the base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY /internal internal
COPY /build/egb/requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run when the container starts
CMD [ "python", "app.py" ]