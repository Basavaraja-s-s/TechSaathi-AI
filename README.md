# TechSaathi AI – Smart Study Copilot

An AI-powered web application designed to assist students with learning activities including AI tutoring, code debugging, exam question generation, study plan creation, and document-based question answering.

## Features

- 💬 **AI Chat**: General tutoring and question answering
- 💻 **Code Debugging**: Analyze code for bugs and suggest improvements
- 📝 **Exam Questions**: Generate practice questions with answers
- 📚 **Study Plans**: Create structured 7-day learning schedules
- 📄 **Document Q&A**: Upload PDFs and ask questions about their content
- 🌓 **Dark/Light Theme**: Comfortable viewing in any lighting condition
- 📊 **Dashboard**: Track your learning statistics

## Tech Stack

- **Backend**: Python FastAPI
- **AI Model**: Groq API (LLaMA 3-8B-8192)
- **Storage**: AWS S3
- **PDF Processing**: pypdf
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Markdown**: marked.js
- **Syntax Highlighting**: highlight.js

## Prerequisites

- Python 3.11 or higher
- AWS Account with S3 access
- Groq API key (get one at https://console.groq.com)

## Installation

1. **Clone or download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual values:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_S3_BUCKET_NAME=techsaathi-documents
   AWS_REGION=us-east-1
   ```

4. **Create S3 Bucket**
   
   Create an S3 bucket in your AWS account with the name specified in `AWS_S3_BUCKET_NAME`.
   Make sure the bucket has appropriate permissions for your AWS credentials.

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The application will be available at: **http://localhost:8000**

## Project Structure

```
techsaathi-ai/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── .env                   # Your environment variables (not in git)
├── services/
│   ├── __init__.py
│   ├── ai_service.py      # Groq API integration
│   ├── pdf_service.py     # PDF text extraction
│   └── s3_service.py      # AWS S3 operations
├── templates/
│   ├── index.html         # Main chat interface
│   └── dashboard.html     # Statistics page
├── static/
│   ├── css/
│   │   └── style.css      # Theme styles and layout
│   └── js/
│       ├── chat.js        # Chat interaction logic
│       ├── upload.js      # File upload handling
│       ├── theme.js       # Theme switching
│       └── markdown.js    # Markdown rendering
└── tests/                 # Test files
```

## Usage

### Chat Modes

1. **Chat Mode**: Ask general questions and get tutoring help
2. **Code Debug Mode**: Paste code to get debugging assistance
3. **Exam Mode**: Request practice questions on any topic
4. **Study Plan Mode**: Get a 7-day study plan for any subject
5. **Document Q&A Mode**: Upload a PDF and ask questions about it

### Uploading Documents

1. Click the "📤 Upload PDF" button in the sidebar
2. Select a PDF file (max 10MB)
3. Wait for the upload and processing to complete
4. The document will appear in the sidebar
5. Click on a document to select it
6. Switch to "Document Q&A" mode to ask questions

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift + Enter**: New line in message input

## API Endpoints

- `GET /` - Main chat interface
- `GET /dashboard` - Statistics dashboard
- `POST /chat` - Process AI chat requests
- `POST /upload-pdf` - Upload PDF documents
- `GET /documents` - List uploaded documents

## Troubleshooting

### Services not initializing

Make sure all environment variables are set correctly in your `.env` file.

### PDF upload fails

- Check that your file is a valid PDF
- Ensure file size is under 10MB
- Verify AWS S3 credentials and bucket permissions

### AI responses not working

- Verify your Groq API key is valid
- Check your internet connection
- Review the logs in `techsaathi.log`

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ --cov=services

# Run specific test file
pytest tests/unit/test_ai_service.py -v
```

### Logs

Application logs are written to `techsaathi.log` in the project root directory.

## License

This project is for educational purposes.

## Support

For issues or questions, please check the logs or review the error messages in the application.
