# 1. Base Image: Start with a lightweight Python environment
FROM python:3.11-slim

# 2. Set Working Directory inside the container
WORKDIR /app

# 3. Copy requirements first (for better caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Initialize the database (Running our script inside the container)
RUN python init_db.py

# 7. Expose the port Flask runs on
EXPOSE 5000

# 8. Command to run the application
CMD ["python", "app.py"]
