FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.10 python3-pip \
        ffmpeg git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

WORKDIR /app

# Install Python dependencies
# torch/torchaudio are installed first with the CUDA index to get GPU-enabled wheels;
# openai-whisper is installed separately so it reuses the already-present torch.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "setuptools>=68,<71" wheel && \
    pip install --no-cache-dir torch==2.6.0 torchaudio==2.6.0 \
        --index-url https://download.pytorch.org/whl/cu124 && \
    pip install --no-cache-dir --no-build-isolation openai-whisper==20240930

# Copy application source
COPY app/ .

# Mount point for user data (input video + output results)
VOLUME ["/data"]
WORKDIR /data

ENTRYPOINT ["python", "/app/main.py"]
CMD ["--help"]
