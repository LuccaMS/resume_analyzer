# Tecnologias e Escolhas do Sistema

## Large Language Model (LLM)

### **Gemini 2.5 Flash** - *Google AI*
A aplicação utiliza o modelo **Gemini 2.5 Flash** através da API oficial do Google, uma escolha estratégica baseada na disponibilidade de **acesso gratuito** para desenvolvimento e testes de projetos.

#### Limites da API Gratuita
| Métrica | Limite |
|---------|--------|
| **RPM** (Requests per minute) | 10 |
| **RPD** (Requests per day) | 250 |
| **TPM** (Tokens per minute) | 250,000 |

> **Por que escolhemos?** O Google oferece uma chave de API gratuita robusta, ideal para prototipagem e desenvolvimento inicial sem custos operacionais.

---

## Modelo de Embedding

### **all-MiniLM-L6-v2** - *Sentence Transformers*
O modelo de embedding é executado **localmente** através da biblioteca `langchain_huggingface`.

**Fonte:** [Hugging Face Model Hub](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

## Banco de Dados Vetorial

### **ChromaDB** - *Vector Database*
O **ChromaDB** é utilizado como solução de armazenamento vetorial, oferecendo busca semântica eficiente, escalabilidade horizontal e integração nativa com Python.

---

## API e Interface

### **FastAPI** 
A aplicação é disponibilizada através do **FastAPI**, proporcionando performance excepcional com suporte assíncrono, documentação automática via Swagger UI e ambiente de testes integrado.

> **Testando a API:** Acesse `/docs` para interagir com todos os endpoints através da interface Swagger UI.

---

## Reconhecimento Óptico de Caracteres (OCR)

### **PaddleOCR** - *Framework de OCR Avançado*
O [**PaddleOCR**](https://github.com/PaddlePaddle/PaddleOCR) é implementado para extração de texto de imagens, executado localmente com suporte tanto para **CPU** quanto para **CUDA (GPU NVIDIA)**, permitindo ao usuário escolher a opção mais adequada ao seu ambiente.
