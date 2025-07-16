# Stage 1: Use an official Python runtime as a parent image
# Using a slim version helps to keep the final image size smaller.
FROM python:3.11-slim

# Set environment variables
# PYTHONUNBUFFERED ensures that Python output is sent straight to the terminal without being buffered first.
ENV PYTHONUNBUFFERED=1
# PYTHONDONTWRITEBYTECODE prevents Python from writing .pyc files to disc.
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file into the container
# This is done first to leverage Docker's layer caching.
# The dependencies layer will only be rebuilt if requirements.txt changes.
COPY ./requirements.txt /code/requirements.txt

# Install the Python dependencies
# --no-cache-dir disables the pip cache to reduce image size.
RUN pip install --no-cache-dir --upgrade pip -r /code/requirements.txt

# Copy the application source code into the container
# This copies the entire 'app' directory which contains main.py and services.py
COPY ./app /code/app

# If you have a .env file you want to include in the image (not recommended for production keys),
# you would copy it here. For production, it's better to use Docker secrets or environment variables.
# COPY ./.env /code/.env

# Expose the port the app runs on
EXPOSE 8001

# Define the command to run the application when the container starts
# We point to 'app.main:app' because main.py is inside the 'app' directory.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]