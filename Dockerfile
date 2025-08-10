# Lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Chrome, ChromeDriver and required runtime dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    # Essential runtime dependencies for Chrome/ChromeDriver
    libnss3 \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxkbcommon0 \
    --no-install-recommends && \
    # Install Chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    # Get Chrome version for logging
    google-chrome --version && \
    # Install ChromeDriver - using latest stable version
    CHROMEDRIVER_VERSION="131.0.6778.204" && \
    echo "Installing ChromeDriver version: $CHROMEDRIVER_VERSION" && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -q /tmp/chromedriver.zip -d /tmp/ && \
    # Make sure we're moving the actual chromedriver binary, not other files
    ls -la /tmp/chromedriver-linux64/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    # Verify installation
    /usr/bin/chromedriver --version && \
    # Cleanup build dependencies only, keep runtime dependencies
    apt-get purge -y wget gnupg unzip && \
    apt-get autoremove -y && \
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
