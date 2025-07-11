# PaddleOCR Docker Setup

- To use **GPU support**, ensure you have CUDA installed on the host.
- In `backend/Dockerfile`, use:

```dockerfile
RUN pip install paddlepaddle-gpu==2.5.0.post112 -f https://paddlepaddle.org.cn/whl/mkl/avx/stable.html
RUN pip install paddleocr
