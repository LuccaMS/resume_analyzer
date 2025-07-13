# ⚠️ Configuração para Ambientes sem GPU NVIDIA

Se você **não possui uma GPU da NVIDIA** em seu ambiente, será necessário fazer algumas alterações na configuração.

## 🔧 Alterações Necessárias

### 1. Configuração do Docker Compose

No arquivo `docker-compose.yml`, você precisará fazer as seguintes alterações:

#### Variáveis de Ambiente:
- `USE_CUDA`: Configure como `False`
- `GEMINI_API_KEY`: Configure com sua chave de API do Gemini (veja a seção [Configuração da API Gemini](#configuração-da-api-gemini))

#### Remover Configuração de GPU:
Você também deve **remover completamente** a seção `deploy` que reserva recursos de GPU:

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
      - GEMINI_API_KEY=sua_chave_aqui
      - USE_CUDA=False
    volumes:
      - ./backend/users.json:/app/users.json
      - ./backend/tmp:/app/tmp
      - ./backend/resumes_processed:/app/resumes_processed
      - ./backend/chroma_langchain_db:/app/chroma_langchain_db
      - ./backend/:/app
    ports:
      - "8000:8000"
    # A seção deploy foi removida para ambientes sem GPU
```

### 2. Alteração no Dockerfile

No arquivo `backend/Dockerfile`, substitua a seguinte seção:

#### ❌ Versão com GPU:
```dockerfile
RUN pip install paddlepaddle-gpu==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/ \
    && pip install paddleocr \
    && pip install sentence-transformers
```

#### ✅ Versão sem GPU (CPU):
```dockerfile
RUN pip install paddlepaddle==3.1.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/ \
    && pip install paddleocr \
    && pip install sentence-transformers
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

No arquivo `docker-compose.yml`, adicione ou configure a variável:

```yaml
environment:
  - USE_CUDA=False
  - GEMINI_API_KEY=sua_chave_de_api_aqui
```

## 📋 Resumo das Alterações

- [ ] Configurar `USE_CUDA=False` no docker-compose.yml
- [ ] Adicionar `GEMINI_API_KEY` com sua chave de API
- [ ] **Remover completamente a seção `deploy` com configurações de GPU**
- [ ] Alterar o Dockerfile para usar paddlepaddle-cpu