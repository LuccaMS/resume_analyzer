# --- Base stage: install dependencies ---
FROM python:3.10 as base

WORKDIR /app

COPY requirements.txt .

# Install lightweight dependencies first
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install heavy OCR libraries only once
RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/ \
 && pip install paddleocr


# --- Final stage: app code only ---
FROM python:3.10

WORKDIR /app

# Copy everything from the base (installed Python packages)
COPY --from=base /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Add only your application source (this is what changes the most)
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
