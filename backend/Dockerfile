# Production Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# For production, copy all source files into the container
COPY . .

# Set production environment
ENV FLASK_ENV=production

EXPOSE 5000

# Run the app in production mode
CMD ["python", "app.py"]
