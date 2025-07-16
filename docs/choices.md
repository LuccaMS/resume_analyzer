# System Technologies and Choices

## Large Language Model (LLM)

### **Gemini 2.5 Flash** - *Google AI*
The application uses the **Gemini 2.5 Flash** model through Google's official API, a strategic choice based on the availability of **free access** for development and testing projects.

#### Free API Limits
| Metric | Limit |
|---------|-------|
| **RPM** (Requests per minute) | 10 |
| **RPD** (Requests per day) | 250 |
| **TPM** (Tokens per minute) | 250,000 |

> **Why did we choose it?** Google offers a robust free API key, ideal for prototyping and initial development without operational costs.

---

## Embedding Model

### **all-MiniLM-L6-v2** - *Sentence Transformers*
The embedding model is executed **locally** through the `langchain_huggingface` library.

**Source:** [Hugging Face Model Hub](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

## Vector Database

### **ChromaDB** - *Vector Database*
**ChromaDB** is used as the vector storage solution, offering efficient semantic search, horizontal scalability, and native Python integration.

---

## API and Interface

### **FastAPI**

The application is made available through **FastAPI**, providing exceptional performance with asynchronous support, automatic documentation via Swagger UI, and integrated testing environment.

> **Testing the API:** Access `/docs` to interact with all endpoints through the Swagger UI interface.

---

## Optical Character Recognition (OCR)

### **PaddleOCR** - *Advanced OCR Framework*
[**PaddleOCR**](https://github.com/PaddlePaddle/PaddleOCR) is implemented for text extraction from images, running locally with support for both **CPU** and **CUDA (NVIDIA GPU)**, allowing users to choose the most suitable option for their environment.