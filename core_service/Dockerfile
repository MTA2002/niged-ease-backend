# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip and install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8001


# Run the Django migrations and then the development server when the container launches
CMD ["sh", "-c", "python manage.py runserver 8001"]