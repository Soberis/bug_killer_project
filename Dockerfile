# Stage 1: Builder
# We use a larger image with build tools to compile dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
# We copy only the installed libraries from the builder stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed python dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Run db init
RUN python init_db.py

EXPOSE 5000

CMD ["python", "app.py"]

