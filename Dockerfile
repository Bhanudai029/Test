# Lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome (minimal set)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY headless_browser.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WDM_LOCAL=1
ENV PORT=10000

# Expose port
EXPOSE 10000

# Run the application with minimal resources
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "2", "--timeout", "120"]
