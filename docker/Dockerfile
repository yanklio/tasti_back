# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements directory and file into the container
COPY src/requirements/ requirements/
COPY src/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY src/ .

# Expose port 8000
EXPOSE 8000

# Set entrypoint script
ENTRYPOINT ["/app/src/entrypoint.sh"]

# Run collectstatic if it exists, otherwise skip
RUN if [ -f manage.py ] && grep -q "django.contrib.staticfiles" config/settings.py; then python manage.py collectstatic --noinput; fi

# Define the command to run your Django application
# This is overridden by docker-compose.yml for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
