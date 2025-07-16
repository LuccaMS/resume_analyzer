# 📋 Aplicação de Gerenciamento de Currículos

## 🎯 Visão Geral

Esta aplicação permite que usuários construam uma base abrangente de currículos e interajam com ela através de consultas em linguagem natural. Recrutadores podem encontrar os melhores candidatos para vagas específicas simplesmente descrevendo seus requisitos em texto livre.

## Escolhas Técnicas

Consulte o arquivo `escolhas.md` para saber mais sobre as decisões técnicas sobre o projeto.

## 🚀 Primeiros Passos

### Pré-requisitos

- Docker instalado em seu sistema
- Configuração do ambiente (consulte `ambiente.md`)

### Instalação e Configuração

1. **Configure seu ambiente** de acordo com as instruções em `ambiente.md`

2. **Construa e execute a aplicação**:
   ```bash
   docker compose up --build
   ```

   > ⚠️ **Nota**: Esta aplicação usa modelos de IA locais, então o processo de build do Docker pode levar um tempo considerável, pois as dependências podem exceder 1GB cada.

3. **Verifique se a aplicação está funcionando**:
   
   Procure por esta saída em seu terminal:
   ```
   backend-1  | INFO:     Started server process [1]
   backend-1  | INFO:     Waiting for application startup.
   backend-1  | INFO:     Application startup complete.
   backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

4. **Acesse a documentação**:
   - Documentação da API: `http://localhost:8000/docs`

## 🔐 Autenticação

### Registro de Usuário

Registre uma nova conta de usuário:

```bash
curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "SEU_USUÁRIO",
  "password": "SUA_SENHA"
}'
```

**Resposta**:
```json
{
  "msg": "User registered",
  "uuid": "753bca1a-3b0e-4583-af61-613945256605"
}
```

> 🔑 **Importante**: Salve o UUID! Ele é necessário para todas as chamadas subsequentes da API.

### Login de Usuário

Faça login para recuperar seu UUID:

```bash
curl -X 'POST' \
  'http://localhost:8000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "SEU_USUÁRIO",
  "password": "SUA_SENHA"
}'
```

**Resposta**:
```json
{
  "msg": "Login successful",
  "uuid": "753bca1a-3b0e-4583-af61-613945256605"
}
```

## 📤 Upload e Processamento

### Upload de Arquivos de Currículo

O endpoint `/upload` realiza OCR e extrai resumos estruturados dos currículos enviados:

```bash
curl -X 'POST' \
  'http://localhost:8000/upload?user_uuid=753bca1a-3b0e-4583-af61-613945256605' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@cv_exemplo.png;type=image/png'
```

**Resposta**:
```json
{
  "json_files": [
    "resumes_processed/nomedousuario.json"
  ]
}
```

> ⚠️ **Nota de Performance**: O processamento baseado em CPU pode ser lento. A aceleração por GPU (testada com GTX 1660Ti) proporciona performance excepcional de OCR.

## 📊 Recuperação de Dados

### Listar Currículos Processados

Recupere dados estruturados paginados dos currículos processados:

```bash
curl -X 'GET' \
  'http://localhost:8000/resumes?limit=10&offset=0' \
  -H 'accept: application/json' \
  -H 'x-token: 753bca1a-3b0e-4583-af61-613945256605'
```

O formato da resposta está detalhado em `rota_resumes_resposta.json`.

## 🤖 Correspondência de Candidatos com IA

### Consultar a Base de Currículos

O endpoint `/question` usa um agente baseado em grafos com acesso a um banco de dados vetorial contendo vetores densos de todos os currículos registrados:

```bash
curl -X 'POST' \
  'http://localhost:8000/question?user_uuid=753bca1a-3b0e-4583-af61-613945256605' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "quero contratar um desenvolvedor React"
}'
```

**Resposta**:
```json
{
  "answer": "### Justificativa de Ranqueamento\n\n**1. Larissa Pereira**\n\nLarissa é a candidata mais adequada para a vaga de desenvolvedor React. Seu currículo a descreve como \"specializing in React and responsive design with a passion for clean UI\", o que demonstra um foco e expertise claros na tecnologia. Além disso, sua experiência como \"Frontend Developer - InovaData (2020-2021): Developed\" indica que ela possui experiência prática e relevante no desenvolvimento de interfaces. A menção de suas habilidades técnicas incluindo \"HTML\", \"CSS\", \"JavaScript\", e \"React\" reforça sua base sólida para a posição.\n\n**2. Lucca Machado**\n\nLucca é um forte segundo candidato, com experiência em \"APIs with front-end interfaces using React and Python\". Embora sua experiência seja mais abrangente, incluindo Python, o que pode ser um diferencial dependendo dos requisitos exatos do projeto, Larissa se destaca por sua especialização explícita em React e design responsivo, que são cruciais para um desenvolvedor React dedicado.\n\n### Arquivos de Currículos Utilizados:\n\n*   larissapereira.json\n*   luccamachado.json",
  "files": [
    "larissapereira.json",
    "luccamachado.json"
  ],
  "file_urls": [
    "http://localhost:8000/downloads/larissapereira.json?user_uuid=753bca1a-3b0e-4583-af61-613945256605",
    "http://localhost:8000/downloads/luccamachado.json?user_uuid=753bca1a-3b0e-4583-af61-613945256605"
  ]
}
```

**Campos da Resposta**:
- `answer`: Resposta gerada pela IA em formato markdown
- `files`: Lista de arquivos de currículo usados para gerar a resposta
- `file_urls`: Links diretos para download de cada currículo mencionado

## 📥 Downloads de Arquivos

### Download de Currículos Processados

O endpoint `/downloads/{filename}` permite baixar qualquer currículo processado:

- Requer autenticação válida por UUID
- O nome do arquivo pode ser obtido nos endpoints `/resumes` ou `/question`
- Links diretos para download são fornecidos nas respostas das consultas

## 🔄 Fluxo de Trabalho da API

1. **Registrar/Login** → Obter UUID
2. **Upload de Currículos** → Processar com OCR + extração por IA
3. **Consultar Base** → Obter candidatos ranqueados com justificativas
4. **Download de Currículos** → Acessar informações detalhadas dos candidatos

## 🛠️ Funcionalidades Técnicas

- **Processamento OCR**: Extrai texto de currículos baseados em imagem
- **Extração por IA**: Estrutura dados de currículos inteligentemente
- **Base de Dados Vetorial**: Permite busca semântica em todos os currículos
- **Agente Baseado em Grafos**: Fornece ranqueamento contextual de candidatos
- **Autenticação Segura**: Validação de usuário baseada em UUID
- **Logging Abrangente**: Rastreia todas as interações do usuário

## 📝 Recursos Adicionais

- **Documentação da API**: Disponível no endpoint `/docs`
- **Detalhes das Rotas**: Consulte `rotas.md` para descrições completas das rotas
- **Configuração do Ambiente**: Siga as instruções em `ambiente.md`
- **Exemplos de Resposta**: Verifique `rota_resumes_resposta.json` para respostas de exemplo
