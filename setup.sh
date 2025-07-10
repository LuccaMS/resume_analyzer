#!/bin/bash

# Setup script for OCR Document Processor
echo "🚀 Setting up OCR Document Processor..."

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p app
mkdir -p data/{uploads,results}
touch data/users.json

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Application specific
data/
uploads/
results/
users.json
hf_model/
Dolphin/

# Docker
.dockerignore
EOF

# Create .dockerignore
echo "🐳 Creating .dockerignore..."
cat > .dockerignore << EOF
.git
.gitignore
README.md
.dockerignore
Dockerfile
docker-compose.yml
.vscode
.idea
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
Thumbs.db
EOF

# Create README
echo "📚 Creating README..."
cat > README.md << EOF
# OCR Document Processor

A Streamlit application with user authentication and OCR processing using ByteDance's Dolphin model.

## Features
- User authentication (register, login, password reset)
- Document upload and OCR processing
- User-specific file storage
- Clean and intuitive interface

## Quick Start

### Using Docker (Recommended)
\`\`\`bash
# Build and run
docker-compose up --build

# Access the application
open http://localhost:8501
\`\`\`

### Manual Setup
\`\`\`bash
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
\`\`\`

## Usage
1. Register a new account or login
2. Upload image files (PNG, JPG, JPEG)
3. Process OCR to extract text
4. View and download results

## Directory Structure
\`\`\`
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
\`\`\`

## Notes
- Model download may take time on first build
- Each user has isolated file storage
- OCR processing requires significant computational resources
EOF

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your Streamlit app to app/main.py"
echo "2. Run: docker-compose up --build"
echo "3. Access: http://localhost:8501"
echo ""
echo "🎉 Happy coding!"