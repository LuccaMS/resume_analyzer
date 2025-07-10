# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Clone Dolphin repository
RUN git clone https://github.com/ByteDance/Dolphin.git

# Install Dolphin requirements
RUN cd Dolphin && pip install -r requirements.txt

# Install huggingface_hub for model download
RUN pip install huggingface_hub

# Download Dolphin model (this might take a while)
RUN mkdir -p hf_model && \
    python -c "from huggingface_hub import snapshot_download; snapshot_download('ByteDance/Dolphin', local_dir='./hf_model')"

# Copy application code
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p uploads results

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port
EXPOSE 8501

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app\n\
streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0\n\
' > start.sh && chmod +x start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["./start.sh"]