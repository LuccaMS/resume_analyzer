# Configuração de ambiente

## 🔧 Alterações Necessárias

### 1. Variáveis de ambiente

Crie um novo arquivo `.env` na pasta raiz do projeto. Dentro deste arquivo, crie duas variáveis, uma chamada `USE_CUDA` e outra chamada `GEMINI_API_KEY`. 

Se você **não possui uma GPU da NVIDIA** em seu ambiente, insira o valor `False` para a variável `USE_CUDA`. Caso contrário, configure o valor desta variável como `True.`


```env
USE_CUDA=False
GEMINI_API_KEY=sua_chave_gemini_aqui
```
ou

```env
USE_CUDA=True
GEMINI_API_KEY=sua_chave_gemini_aqui
```

### 2. Configuração do Docker Compose

#### Configuração de GPU:
Se você **não possui uma GPU da NVIDIA** em seu ambiente você deve **remover completamente** a seção `deploy` que reserva recursos de GPU:

#### ❌ Remover esta seção:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

#### ✅ Configuração correta para CPU:
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
    # A seção deploy foi removida para ambientes sem GPU
  frontend:
    build: ./frontend
    container_name: streamlit_frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```
#### ✅ Configuração correta para GPU CUDA NVIDIA:
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


### 3. Alteração no Dockerfile

No arquivo `backend/Dockerfile`, se você **não possui uma GPU da NVIDIA** modifique o seu Dockerfile para que ele fique assim:

#### Versão sem GPU (CPU):
```dockerfile
# Installing PaddleOCR and its heavy dependencies
#RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
# && pip install paddleocr \
# && pip install sentence-transformers

RUN pip install paddlepaddle==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ \
    && pip install paddleocr \
    && pip install sentence-transformers
```

Se você  **possui uma GPU da NVIDIA** configure o seu Dockerfile desta maneira :

#### Versão com GPU:
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

## 🔑 Configuração da API Gemini

Para configurar sua chave de API do Gemini, siga os passos abaixo:

### 1. Obter a Chave de API

1. Acesse o [Google AI Studio](https://aistudio.google.com/)
2. Faça login com sua conta Google
3. Clique em "Get API Key" ou "Obter chave de API"
4. Crie um novo projeto ou selecione um existente
5. Copie sua chave de API

### 2. Configurar a Variável de Ambiente

No arquivo `.env` que você criou anteriormente, mude a variável `GEMINI_API_KEY` para a sua chave de api conforme o exemplo abaixo, não insira nenhum caráctere adicional.

```env
USE_CUDA=False
GEMINI_API_KEY=2114cf82-d4d2-4d1c-8c9f-500fb6ab897b
```