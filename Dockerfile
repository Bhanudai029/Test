# Lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Chrome and ChromeDriver manually
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    --no-install-recommends && \
    # Install Chrome
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable --no-install-recommends && \
    # Get Chrome version and install matching ChromeDriver
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1) && \
    wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O /tmp/chromedriver_version && \
    CHROMEDRIVER_VERSION=$(cat /tmp/chromedriver_version) && \
    wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -q /tmp/chromedriver.zip -d /usr/bin/ && \
    chmod +x /usr/bin/chromedriver && \
    # Cleanup to reduce image size
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
