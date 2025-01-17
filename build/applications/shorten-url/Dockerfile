# Use the official Python base image with Alpine Linux
FROM 0x1115/egb:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY /applications/shorten_url/requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the application code to the container
COPY . .

# Expose the port on which the Flask application will run
EXPOSE 8080

# Set the entrypoint command to run the Flask application
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]