# TechSaathi AI - Complete Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Get Your API Keys

#### Groq API Key
1. Go to https://console.groq.com
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key

#### AWS S3 Setup
1. Log in to AWS Console
2. Go to IAM → Users → Create User
3. Attach policy: `AmazonS3FullAccess`
4. Create access key
5. Copy Access Key ID and Secret Access Key
6. Go to S3 → Create Bucket
7. Name it (e.g., `techsaathi-documents`)
8. Choose your region (e.g., `us-east-1`)
9. Keep default settings and create

### Step 3: Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
AWS_ACCESS_KEY_ID=AKIA_your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_S3_BUCKET_NAME=techsaathi-documents
AWS_REGION=us-east-1
APP_ENV=development
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=application/pdf
```

### Step 4: Run the Application

```bash
uvicorn main:app --reload
```

Or on Windows, double-click `start.bat`

### Step 5: Open in Browser

Navigate to: http://localhost:8000

## Detailed Setup Instructions

### Python Version

Make sure you have Python 3.11 or higher:

```bash
python --version
```

If you need to install Python:
- Windows: Download from https://www.python.org/downloads/
- Mac: `brew install python@3.11`
- Linux: `sudo apt install python3.11`

### Virtual Environment (Recommended)

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### AWS S3 Bucket Permissions

Your S3 bucket needs these permissions:
- `s3:PutObject` - Upload files
- `s3:GetObject` - Read files
- `s3:ListBucket` - List files

You can use this IAM policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::techsaathi-documents",
                "arn:aws:s3:::techsaathi-documents/*"
            ]
        }
    ]
}
```

### Troubleshooting

#### "Module not found" errors

```bash
pip install -r requirements.txt --upgrade
```

#### "Services not initialized" error

Check your `.env` file:
- Make sure all keys are present
- No extra spaces around `=`
- Keys are not wrapped in quotes
- File is named exactly `.env` (not `.env.txt`)

#### AWS S3 errors

- Verify bucket name matches exactly
- Check AWS credentials are correct
- Ensure bucket is in the correct region
- Verify IAM user has S3 permissions

#### Groq API errors

- Verify API key is valid
- Check you haven't exceeded rate limits
- Ensure you have credits/quota available

### Testing the Setup

1. Start the server
2. Open http://localhost:8000
3. You should see the TechSaathi AI interface
4. Try sending a message in Chat mode
5. Try uploading a small PDF

### Development Mode

The application runs in development mode by default with:
- Auto-reload on code changes
- Detailed error messages
- Console logging

### Production Deployment

For production:

1. Set `APP_ENV=production` in `.env`
2. Use a production WSGI server
3. Set up proper logging
4. Configure CORS appropriately
5. Use environment-specific secrets

## Features Overview

### 1. Chat Mode
- General tutoring
- Question answering
- Concept explanations

### 2. Code Debug Mode
- Paste your code
- Get bug analysis
- Receive improvement suggestions

### 3. Exam Mode
- Specify a topic
- Get 5 practice questions
- Includes answers

### 4. Study Plan Mode
- Specify a subject
- Get a 7-day structured plan
- Organized by day

### 5. Document Q&A Mode
- Upload PDF documents
- Ask questions about content
- AI answers based on document

## Tips for Best Results

### For Code Debugging
- Include the full code context
- Mention the programming language
- Describe what you expect vs what happens

### For Exam Questions
- Be specific about the topic
- Mention difficulty level if needed
- Specify question type (MCQ, short answer, etc.)

### For Study Plans
- Mention your current level
- Specify any time constraints
- Include specific topics to cover

### For Document Q&A
- Upload clear, text-based PDFs
- Ask specific questions
- Reference page numbers if needed

## Support

If you encounter issues:

1. Check `techsaathi.log` for error details
2. Verify all environment variables
3. Test API keys independently
4. Review the README.md

## Next Steps

- Explore all 5 modes
- Upload some study materials
- Check the Dashboard for statistics
- Try both light and dark themes

Happy learning with TechSaathi AI! 🎓
