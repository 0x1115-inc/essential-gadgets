# Use the official Python base image with Alpine Linux
FROM 0x1115/egb:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the application code to the container
COPY . .

# Expose the port on which the Flask application will run
ENV PORT=8080
EXPOSE $PORT

# Set the entrypoint command to run the Flask application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app