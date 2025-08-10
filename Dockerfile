# Lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    --no-install-recommends && \
    # Add Google Chrome's official GPG key and repository
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list && \
    # Update and install Chrome
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    # Verify Chrome installation
    google-chrome --version && \
    # Install ChromeDriver - using latest stable version
    CHROMEDRIVER_VERSION="131.0.6778.204" && \
    echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    # Verify ChromeDriver installation
    /usr/bin/chromedriver --version && \
    # Clean up
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
