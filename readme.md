# 📋 Resume Management Application

## 🎯 Overview

This application allows users to build a comprehensive resume database and interact with it through natural language queries. Recruiters can find the best candidates for specific positions simply by describing their requirements in free text.

## Visual Interface

If you're only interested in interacting with the graphical interface, follow the project execution steps and environment variable configuration. After that, access the following address: http://localhost:8501/. There, you will find the Streamlit interface to interact with the application.

## Technical Choices

Check the [`choices.md`](docs/choices.md) file to learn more about the technical decisions regarding the project.

## 🚀 Getting Started

### Prerequisites

- Docker installed on your system
- Environment configuration (see [`environment.md`](docs/environment.md))

### Installation and Setup

1. **Configure your environment** according to the instructions in [`environment.md`](docs/environment.md)

2. **Build and run the application**:
   ```bash
   docker compose up --build
   ```

   > ⚠️ **Note**: This application uses local AI models, so the Docker build process may take considerable time, as dependencies can exceed 1GB each.

3. **Verify the application is running**:
   
   Look for this output in your terminal:
   ```
   backend-1  | INFO:     Started server process [1]
   backend-1  | INFO:     Waiting for application startup.
   backend-1  | INFO:     Application startup complete.
   backend-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   ```

4. **Access the documentation**:
   - API Documentation: `http://localhost:8000/docs`

## 🔐 Authentication

### User Registration

Register a new user account:

```bash
curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD"
}'
```

**Response**:
```json
{
  "msg": "User registered",
  "uuid": "753bca1a-3b0e-4583-af61-613945256605"
}
```

> 🔑 **Important**: Save the UUID! It's required for all subsequent API calls.

### User Login

Login to retrieve your UUID:

```bash
curl -X 'POST' \
  'http://localhost:8000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD"
}'
```

**Response**:
```json
{
  "msg": "Login successful",
  "uuid": "753bca1a-3b0e-4583-af61-613945256605"
}
```

## 📤 Upload and Processing

### Resume File Upload

The `/upload` endpoint performs OCR and extracts structured summaries from uploaded resumes:

```bash
curl -X 'POST' \
  'http://localhost:8000/upload?user_uuid=753bca1a-3b0e-4583-af61-613945256605' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@cv_example.png;type=image/png'
```

**Response**:
```json
{
  "json_files": [
    "resumes_processed/username.json"
  ]
}
```

> ⚠️ **Performance Note**: CPU-based processing can be slow. GPU acceleration (tested with GTX 1660Ti) provides exceptional OCR performance.

## 📊 Data Retrieval

### List Processed Resumes

Retrieve paginated structured data from processed resumes:

```bash
curl -X 'GET' \
  'http://localhost:8000/resumes?limit=10&offset=0' \
  -H 'accept: application/json' \
  -H 'x-token: 753bca1a-3b0e-4583-af61-613945256605'
```

The response format is detailed in `resumes_route_response.json`.

## 🤖 AI Candidate Matching

### Query the Resume Database

The `/question` endpoint uses a graph-based agent with access to a vector database containing dense vectors of all registered resumes:

```bash
curl -X 'POST' \
  'http://localhost:8000/question?user_uuid=753bca1a-3b0e-4583-af61-613945256605' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "I want to hire a React developer"
}'
```

**Response**:
```json
{
  "answer": "### Ranking Justification\n\n**1. Larissa Pereira**\n\nLarissa is the most suitable candidate for the React developer position. Her resume describes her as \"specializing in React and responsive design with a passion for clean UI\", which demonstrates clear focus and expertise in the technology. Additionally, her experience as \"Frontend Developer - InovaData (2020-2021): Developed\" indicates she has practical and relevant experience in interface development. The mention of her technical skills including \"HTML\", \"CSS\", \"JavaScript\", and \"React\" reinforces her solid foundation for the position.\n\n**2. Lucca Machado**\n\nLucca is a strong second candidate, with experience in \"APIs with front-end interfaces using React and Python\". While his experience is more comprehensive, including Python, which could be an advantage depending on the exact project requirements, Larissa stands out for her explicit specialization in React and responsive design, which are crucial for a dedicated React developer.\n\n### Resume Files Used:\n\n*   larissapereira.json\n*   luccamachado.json",
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

**Response Fields**:
- `answer`: AI-generated response in markdown format
- `files`: List of resume files used to generate the response
- `file_urls`: Direct download links for each mentioned resume

## 📥 File Downloads

### Download Processed Resumes

The `/downloads/{filename}` endpoint allows downloading any processed resume:

- Requires valid UUID authentication
- Filename can be obtained from `/resumes` or `/question` endpoints
- Direct download links are provided in query responses

## 🔄 API Workflow

1. **Register/Login** → Get UUID
2. **Upload Resumes** → Process with OCR + AI extraction
3. **Query Database** → Get ranked candidates with justifications
4. **Download Resumes** → Access detailed candidate information

## 🛠️ Technical Features

- **OCR Processing**: Extracts text from image-based resumes
- **AI Extraction**: Intelligently structures resume data
- **Vector Database**: Enables semantic search across all resumes
- **Graph-Based Agent**: Provides contextual candidate ranking
- **Secure Authentication**: UUID-based user validation
- **Comprehensive Logging**: Tracks all user interactions

## 📝 Additional Resources

- **API Documentation**: Available at `/docs` endpoint
- **Environment Setup**: Follow instructions in `environment.md`
- **Response Examples**: Check `resumes_route_response.json` for example responses