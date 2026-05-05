FROM python:3.10-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ .

# Mount point for user data (input video + output results)
VOLUME ["/data"]
WORKDIR /data

ENTRYPOINT ["python", "/app/main.py"]
CMD ["--help"]
