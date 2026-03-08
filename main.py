from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

from services.ai_service import AIService
from services.pdf_service import PDFService
from services.s3_service import S3Service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('techsaathi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="TechSaathi AI - Smart Study Copilot")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize services
try:
    ai_service = AIService(api_key=os.getenv("GROQ_API_KEY"))
    s3_service = S3Service(
        bucket_name=os.getenv("AWS_S3_BUCKET_NAME"),
        aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region=os.getenv("AWS_REGION", "us-east-1")
    )
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    ai_service = None
    s3_service = None

# Statistics counters
stats = {
    "total_chats": 0,
    "total_study_plans": 0,
    "total_exams": 0,
    "total_code_debugs": 0,
    "total_timetables": 0
}

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    mode: str
    document_context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    mode: str
    timestamp: str

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc) if os.getenv("APP_ENV") == "development" else None,
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/")
async def root(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process AI chat requests"""
    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Validate mode
    if request.mode not in ['chat', 'code', 'exam', 'study_plan', 'timetable', 'document']:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {request.mode}")
    
    # Validate document context for document mode
    if request.mode == 'document' and not request.document_context:
        raise HTTPException(status_code=400, detail="Document context required for document mode")
    
    # Check if AI service is initialized
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not available")
    
    try:
        # Generate AI response
        response = await ai_service.generate_response(
            message=request.message,
            mode=request.mode,
            document_context=request.document_context
        )
        
        # Update statistics
        stats["total_chats"] += 1
        if request.mode == 'study_plan':
            stats["total_study_plans"] += 1
        elif request.mode == 'exam':
            stats["total_exams"] += 1
        elif request.mode == 'code':
            stats["total_code_debugs"] += 1
        elif request.mode == 'timetable':
            stats["total_timetables"] += 1
        
        return ChatResponse(
            response=response,
            mode=request.mode,
            timestamp=datetime.utcnow().isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Handle PDF file uploads - optimized for speed"""
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file content
    file_bytes = await file.read()
    
    # Validate file size (10MB limit)
    max_size = 10 * 1024 * 1024
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    # Check if services are initialized
    if not s3_service:
        raise HTTPException(status_code=503, detail="Storage service not available")
    
    try:
        # Run S3 upload and text extraction in parallel for speed
        import asyncio
        upload_task = s3_service.upload_file(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type="application/pdf"
        )
        extract_task = PDFService.extract_text(file_bytes)
        
        # Wait for both to complete
        s3_url, extracted_text = await asyncio.gather(upload_task, extract_task)
        
        return {
            "filename": file.filename,
            "s3_url": s3_url,
            "summary": f"PDF ready - {len(extracted_text)} characters",
            "extracted_text": extracted_text,
            "uploaded_at": datetime.utcnow().isoformat(),
            "size": len(file_bytes)
        }
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    """List all uploaded documents"""
    if not s3_service:
        raise HTTPException(status_code=503, detail="Storage service not available")
    
    try:
        documents = await s3_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Documents endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from S3"""
    if not s3_service:
        raise HTTPException(status_code=503, detail="Storage service not available")
    
    try:
        await s3_service.delete_file(filename)
        return {"message": "Document deleted successfully", "filename": filename}
    except Exception as e:
        logger.error(f"Delete endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{filename}/content")
async def get_document_content(filename: str):
    """Get document content and summary on-demand"""
    if not s3_service:
        raise HTTPException(status_code=503, detail="Storage service not available")
    
    try:
        # Download from S3
        response = s3_service.s3_client.get_object(
            Bucket=s3_service.bucket_name,
            Key=filename
        )
        file_bytes = response['Body'].read()
        
        # Extract text
        extracted_text = await PDFService.extract_text(file_bytes)
        
        return {
            "filename": filename,
            "extracted_text": extracted_text,
            "size": len(extracted_text)
        }
    except Exception as e:
        logger.error(f"Get content endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def dashboard(request: Request):
    """Serve the dashboard page"""
    # Calculate statistics
    total_documents = 0
    if s3_service:
        try:
            documents = await s3_service.list_documents()
            total_documents = len(documents)
        except:
            pass
    
    dashboard_stats = {
        "total_documents": total_documents,
        "total_chats": stats["total_chats"],
        "total_study_plans": stats["total_study_plans"],
        "total_exams": stats["total_exams"],
        "total_code_debugs": stats["total_code_debugs"],
        "total_timetables": stats["total_timetables"]
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": dashboard_stats
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
