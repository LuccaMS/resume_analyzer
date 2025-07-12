# --- Base Python dependencies (light) ---
FROM python:3.10 AS base

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


# --- OCR dependencies stage (heavy, rarely changes) ---
FROM base AS ocr

# Installing PaddleOCR and its heavy dependencies
RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/ \
 && pip install paddleocr


# --- Final image stage ---
FROM python:3.10

# Install required system packages (for OpenCV to work)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libfontconfig1 \
    libxrender1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all installed dependencies
COPY --from=ocr /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=ocr /usr/local/bin /usr/local/bin

# Copy only your application code
COPY . .

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
