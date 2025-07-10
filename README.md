# OCR Document Processor

A Streamlit application with user authentication and OCR processing using ByteDance's Dolphin model.

## Features
- User authentication (register, login, password reset)
- Document upload and OCR processing
- User-specific file storage
- Clean and intuitive interface

## Quick Start

### Using Docker (Recommended)
```bash
# Build and run
docker-compose up --build

# Access the application
open http://localhost:8501
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Clone Dolphin model
git clone https://github.com/ByteDance/Dolphin.git
cd Dolphin
pip install -r requirements.txt
cd ..

# Download model weights
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('ByteDance/Dolphin', local_dir='./hf_model')"

# Run the application
streamlit run app/main.py
```

## Usage
1. Register a new account or login
2. Upload image files (PNG, JPG, JPEG)
3. Process OCR to extract text
4. View and download results

## Directory Structure
```
project/
├── app/
│   └── main.py          # Main Streamlit application
├── data/
│   ├── uploads/         # User uploaded files
│   ├── results/         # OCR results
│   └── users.json       # User data
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Notes
- Model download may take time on first build
- Each user has isolated file storage
- OCR processing requires significant computational resources
