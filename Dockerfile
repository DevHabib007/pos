# Use official Python image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Django server (for testing; in prod use gunicorn)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
