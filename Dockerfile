FROM python:3.10

# Install system dependencies for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    libx11-xcb1 \
    libxcursor1 \
    libxi6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all necessary files into the container
COPY requirements.txt proxies.txt.rename user_agents.txt poo7er.py entrypoint.sh .env /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Keep playwright dep management in Dockerfile for ease of use)
RUN playwright install

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]
