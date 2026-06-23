# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code into the container
# This places the content of your local 'backend' directory into the container's /app directory
COPY ./backend/ ./

# Command to run the application from the new WORKDIR.
# The app is now found at 'app.main' relative to the WORKDIR.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
