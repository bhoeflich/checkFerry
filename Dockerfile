# Use the official Playwright Python image which includes browsers
# Check https://mcr.microsoft.com/en-us/product/playwright/python/tags for latest tags
FROM mcr.microsoft.com/playwright/python:v1.57.0-noble

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1
# ENV TARGET_DATES="2026-01-02,2026-01-03"
# ENV NTFY_TOPIC="your_unique_topic_name"

# Run the application
CMD ["python", "main.py"]
