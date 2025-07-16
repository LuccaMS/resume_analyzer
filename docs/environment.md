# Environment Setup

## 🔧 Required Changes

### 1. Environment Variables

Create a new `.env` file in the project root folder. Inside this file, create two variables, one called `USE_CUDA` and another called `GEMINI_API_KEY`.

If you **do not have an NVIDIA GPU** in your environment, set the value `False` for the `USE_CUDA` variable. Otherwise, configure the value of this variable as `True`.

```env
USE_CUDA=False
GEMINI_API_KEY=your_gemini_key_here
```
or

```env
USE_CUDA=True
GEMINI_API_KEY=your_gemini_key_here
```

### 2. Docker Compose Configuration

#### GPU Configuration:
If you **do not have an NVIDIA GPU** in your environment, you must **completely remove** the `deploy` section that reserves GPU resources:

#### ❌ Remove this section:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

#### ✅ Correct configuration for CPU:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_CUDA=${USE_CUDA}
    volumes:
      - ./backend/users.json:/app/users.json
      - ./backend/tmp:/app/tmp 
      - ./backend/resumes_processed:/app/resumes_processed 
      - ./backend/chroma_langchain_db:/app/chroma_langchain_db
      - ./backend/:/app   
    ports:
      - "8000:8000"
    # The deploy section was removed for environments without GPU
  frontend:
    build: ./frontend
    container_name: streamlit_frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```
#### ✅ Correct configuration for NVIDIA CUDA GPU:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_CUDA=${USE_CUDA}
    volumes:
      - ./backend/users.json:/app/users.json
      - ./backend/tmp:/app/tmp 
      - ./backend/resumes_processed:/app/resumes_processed 
      - ./backend/chroma_langchain_db:/app/chroma_langchain_db
      - ./backend/:/app   
    ports:
      - "8000:8000"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
              
  frontend:
    build: ./frontend
    container_name: streamlit_frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

### 3. Dockerfile Changes

In the `backend/Dockerfile` file, if you **do not have an NVIDIA GPU**, modify your Dockerfile so it looks like this:

#### Version without GPU (CPU):
```dockerfile
# Installing PaddleOCR and its heavy dependencies
#RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
# && pip install paddleocr \
# && pip install sentence-transformers

RUN pip install paddlepaddle==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ \
    && pip install paddleocr \
    && pip install sentence-transformers
```

If you **have an NVIDIA GPU**, configure your Dockerfile this way:

#### Version with GPU:
```dockerfile
# Installing PaddleOCR and its heavy dependencies
RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
 && pip install paddleocr \
 && pip install sentence-transformers

#RUN pip install paddlepaddle==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ \
#    && pip install paddleocr \
#    && pip install sentence-transformers

```
---

## 🔑 Gemini API Configuration

To configure your Gemini API key, follow the steps below:

### 1. Get the API Key

1. Access [Google AI Studio](https://aistudio.google.com/)
2. Log in with your Google account
3. Click on "Get API Key"
4. Create a new project or select an existing one
5. Copy your API key

### 2. Configure the Environment Variable

In the `.env` file you created earlier, change the `GEMINI_API_KEY` variable to your API key as shown in the example below, do not insert any additional characters.

```env
USE_CUDA=False
GEMINI_API_KEY=2114cf82-d4d2-4d1c-8c9f-500fb6ab897b
```