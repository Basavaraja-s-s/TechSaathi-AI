# Design Document

## Overview

TechSaathi AI – Smart Study Copilot is a web-based AI tutoring application built with FastAPI backend and vanilla JavaScript frontend. The system integrates Groq's LLaMA 3 model for AI capabilities, AWS S3 for document storage, and pypdf for PDF text extraction. The architecture follows a service-oriented design with clear separation between AI processing, document management, and user interface components.

The application provides five specialized modes of interaction:
- **Chat Mode**: General tutoring and question answering
- **Code Mode**: Code debugging and improvement suggestions
- **Exam Mode**: Practice question generation with answers
- **Study Plan Mode**: 7-day structured learning schedules
- **Document Mode**: PDF-based question answering using uploaded materials

The frontend uses a single-page application approach with dynamic content updates, markdown rendering, syntax highlighting, and theme customization. All user interactions flow through RESTful API endpoints that coordinate between services to deliver AI-powered responses.

## Architecture

### System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[HTML/CSS/JS Interface]
        Chat[Chat Workspace]
        Sidebar[Document Sidebar]
        Dashboard[Statistics Dashboard]
    end
    
    subgraph "Backend Layer - FastAPI"
        Router[API Router]
        ChatEndpoint[/chat POST]
        UploadEndpoint[/upload-pdf POST]
        DocsEndpoint[/documents GET]
        DashEndpoint[/dashboard GET]
    end
    
    subgraph "Service Layer"
        AIService[AI Service]
        PDFService[PDF Service]
        S3Service[S3 Service]
    end
    
    subgraph "External Services"
        Groq[Groq API - LLaMA 3]
        S3[AWS S3 Storage]
    end
    
    UI --> Router
    Chat --> ChatEndpoint
    Sidebar --> UploadEndpoint
    Sidebar --> DocsEndpoint
    Dashboard --> DashEndpoint
    
    ChatEndpoint --> AIService
    UploadEndpoint --> PDFService
    UploadEndpoint --> S3Service
    DocsEndpoint --> S3Service
    
    AIService --> Groq
    S3Service --> S3
    PDFService --> S3Service
```

### Directory Structure

```
techsaathi-ai-study-copilot/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── services/
│   ├── __init__.py
│   ├── ai_service.py      # Groq API integration
│   ├── pdf_service.py     # PDF text extraction
│   └── s3_service.py      # AWS S3 operations
├── templates/
│   ├── index.html         # Main chat interface
│   └── dashboard.html     # Statistics page
└── static/
    ├── css/
    │   └── style.css      # Theme styles and layout
    └── js/
        ├── chat.js        # Chat interaction logic
        ├── upload.js      # File upload handling
        ├── theme.js       # Theme switching
        └── markdown.js    # Markdown rendering
```

### Technology Stack

- **Backend Framework**: FastAPI 0.104+
- **AI Model**: Groq LLaMA 3 (llama3-8b-8192)
- **PDF Processing**: pypdf 3.17+
- **Cloud Storage**: AWS S3 via boto3
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Markdown Rendering**: marked.js library
- **Syntax Highlighting**: highlight.js library
- **HTTP Client**: Fetch API

## Components and Interfaces

### Backend Components

#### 1. FastAPI Application (main.py)

The main application file initializes FastAPI, configures CORS, serves static files, and defines all API routes.

**Responsibilities:**
- Application initialization and configuration
- Route registration and request handling
- Static file serving (CSS, JS)
- Template rendering (Jinja2)
- Error handling middleware

**Key Routes:**
```python
GET  /                    # Serve main chat interface
GET  /dashboard           # Serve statistics dashboard
POST /chat                # Process AI chat requests
POST /upload-pdf          # Handle PDF uploads
GET  /documents           # List uploaded documents
```

#### 2. AI Service (services/ai_service.py)

Manages all interactions with the Groq API and implements mode-specific prompt engineering.

**Interface:**
```python
class AIService:
    def __init__(self, api_key: str)
    
    async def generate_response(
        self,
        message: str,
        mode: str,
        document_context: Optional[str] = None
    ) -> str:
        """
        Generate AI response based on mode and context.
        
        Args:
            message: User input message
            mode: One of ['chat', 'code', 'exam', 'study_plan', 'document']
            document_context: Extracted PDF text (required for document mode)
            
        Returns:
            AI-generated response string
            
        Raises:
            GroqAPIError: If API request fails
            ValueError: If mode is invalid or document_context missing for document mode
        """
```

**Mode-Specific Prompts:**

- **Chat Mode**: "You are TechSaathi, a helpful AI tutor. Provide clear, educational responses to student questions."

- **Code Mode**: "You are a code debugging assistant. Analyze the provided code for syntax errors, logical bugs, and suggest improvements. Explain what the code does and provide corrected versions."

- **Exam Mode**: "Generate exactly 5 exam questions on the given topic. Format as: Question 1: [question]\nAnswer: [answer]\n\nQuestion 2: ..."

- **Study Plan Mode**: "Create a detailed 7-day study plan for the given subject. Format as: Day 1: [topics/activities]\nDay 2: ..."

- **Document Mode**: "Answer the question based ONLY on the following document content: {document_context}\n\nQuestion: {message}"

#### 3. PDF Service (services/pdf_service.py)

Extracts text content from uploaded PDF files using pypdf library.

**Interface:**
```python
class PDFService:
    @staticmethod
    async def extract_text(file_bytes: bytes) -> str:
        """
        Extract text from PDF file bytes.
        
        Args:
            file_bytes: Raw PDF file content
            
        Returns:
            Extracted text from all pages concatenated
            
        Raises:
            PDFExtractionError: If PDF is corrupted or unreadable
        """
    
    @staticmethod
    def _extract_page_text(page) -> str:
        """Extract text from a single PDF page, handling errors gracefully."""
```

**Implementation Details:**
- Uses pypdf.PdfReader for parsing
- Iterates through all pages sequentially
- Skips pages with no extractable text
- Preserves paragraph structure with newlines
- Returns empty string if no text found

#### 4. S3 Service (services/s3_service.py)

Manages document storage and retrieval from AWS S3.

**Interface:**
```python
class S3Service:
    def __init__(
        self,
        bucket_name: str,
        aws_access_key: str,
        aws_secret_key: str,
        region: str = "us-east-1"
    )
    
    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str = "application/pdf"
    ) -> str:
        """
        Upload file to S3 bucket.
        
        Args:
            file_bytes: File content as bytes
            filename: Name to store file under
            content_type: MIME type of file
            
        Returns:
            Public URL of uploaded file
            
        Raises:
            S3UploadError: If upload fails
        """
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the S3 bucket.
        
        Returns:
            List of document metadata dictionaries with keys:
            - filename: str
            - url: str
            - uploaded_at: str (ISO format)
            - size: int (bytes)
        """
    
    async def get_document_url(self, filename: str) -> str:
        """Get public URL for a specific document."""
```

### Frontend Components

#### 1. Chat Interface (static/js/chat.js)

Manages chat message display, user input, and API communication.

**Key Functions:**
```javascript
class ChatManager {
    constructor() {
        this.messages = [];
        this.currentMode = 'chat';
        this.selectedDocument = null;
    }
    
    async sendMessage(message) {
        // Add user message to UI
        // Show typing indicator
        // Call /chat API endpoint
        // Display AI response
        // Handle errors
    }
    
    addMessage(content, isUser) {
        // Create message bubble
        // Apply styling based on sender
        // Add to chat container
        // Scroll to bottom
    }
    
    showTypingIndicator() { }
    hideTypingIndicator() { }
    
    setMode(mode) {
        // Update current mode
        // Update UI mode selector
    }
    
    clearChat() {
        // Remove all messages
        // Reset state
    }
}
```

#### 2. Upload Handler (static/js/upload.js)

Manages PDF file uploads and document list display.

**Key Functions:**
```javascript
class UploadManager {
    constructor() {
        this.documents = [];
    }
    
    async uploadPDF(file) {
        // Validate file type and size
        // Create FormData
        // POST to /upload-pdf
        // Update document list
        // Show success/error notification
    }
    
    async loadDocuments() {
        // GET from /documents
        // Populate sidebar list
    }
    
    selectDocument(filename) {
        // Highlight selected document
        // Load document context
        // Update chat manager
    }
}
```

#### 3. Theme Manager (static/js/theme.js)

Handles dark/light theme switching and persistence.

**Key Functions:**
```javascript
class ThemeManager {
    constructor() {
        this.currentTheme = this.loadTheme();
    }
    
    toggleTheme() {
        // Switch between dark and light
        // Apply CSS variables
        // Save to localStorage
        // Animate transition
    }
    
    loadTheme() {
        // Read from localStorage
        // Default to dark theme
    }
    
    applyTheme(theme) {
        // Set CSS custom properties
        // Update toggle button state
    }
}
```

#### 4. Markdown Renderer (static/js/markdown.js)

Renders markdown and code blocks in AI responses.

**Key Functions:**
```javascript
class MarkdownRenderer {
    static render(text) {
        // Parse markdown using marked.js
        // Apply syntax highlighting with highlight.js
        // Return HTML string
    }
    
    static highlightCode(code, language) {
        // Apply language-specific highlighting
    }
}
```

## Data Models

### Request/Response Models

#### Chat Request
```json
{
  "message": "string (required, non-empty)",
  "mode": "string (required, one of: chat|code|exam|study_plan|document)",
  "document_context": "string (optional, required when mode=document)"
}
```

#### Chat Response
```json
{
  "response": "string (AI-generated content)",
  "mode": "string (echo of request mode)",
  "timestamp": "string (ISO 8601 format)"
}
```

#### Upload Request
- Content-Type: multipart/form-data
- Field: `file` (PDF file, max 10MB)

#### Upload Response
```json
{
  "filename": "string",
  "s3_url": "string",
  "summary": "string (AI-generated document summary)",
  "extracted_text": "string (full text content)",
  "uploaded_at": "string (ISO 8601 format)",
  "size": "integer (bytes)"
}
```

#### Documents List Response
```json
{
  "documents": [
    {
      "filename": "string",
      "url": "string",
      "uploaded_at": "string",
      "size": "integer"
    }
  ]
}
```

#### Dashboard Statistics Response
```json
{
  "total_documents": "integer",
  "total_chats": "integer",
  "total_study_plans": "integer",
  "total_exams": "integer",
  "total_code_debugs": "integer"
}
```

#### Error Response
```json
{
  "error": "string (error message)",
  "detail": "string (optional, additional context)",
  "status_code": "integer"
}
```

### Internal Data Structures

#### Message Object (Frontend)
```javascript
{
  id: string,           // Unique identifier
  content: string,      // Message text
  isUser: boolean,      // True for user messages
  timestamp: Date,      // Creation time
  mode: string         // Mode when sent
}
```

#### Document Object (Frontend)
```javascript
{
  filename: string,
  url: string,
  uploadedAt: Date,
  size: number,
  extractedText: string,  // Cached for document mode
  summary: string
}
```

### Environment Configuration

Required environment variables (`.env` file):

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET_NAME=techsaathi-documents
AWS_REGION=us-east-1

# Application Configuration
APP_ENV=development
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=application/pdf
```

### Database/Storage Strategy

This application uses a **stateless architecture** with no persistent database:

- **Chat History**: Stored in browser memory (JavaScript array), cleared on page refresh
- **Documents**: Stored in AWS S3 with metadata retrieved via S3 API
- **Statistics**: Calculated on-demand from S3 object counts and in-memory counters
- **Theme Preference**: Stored in browser localStorage
- **Session State**: Maintained client-side only

This approach simplifies deployment and reduces infrastructure requirements while meeting the application's needs for a learning tool where persistent chat history is not critical.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified the following redundancies:

- **2.3 and 12.1**: Both test that exam mode generates exactly 5 questions - these are identical and can be combined
- **2.4 and 13.1**: Both test that study plan mode generates a 7-day plan - these are identical and can be combined
- **2.5 and 4.5**: Both test that document mode uses document context - these are identical and can be combined
- **3.2 and 15.3**: Both test multi-page PDF text extraction - 15.3 is more specific and subsumes 3.2
- **1.5 and 1.6**: Both test rendering capabilities - can be combined into a single comprehensive rendering property
- **8.4 and 8.5**: Both test message display properties - can be verified together as message rendering requirements

The following properties represent the unique, non-redundant correctness requirements:

### Property 1: Message Display Round Trip

*For any* non-empty user message, when submitted to the chat workspace, the message should appear in the chat area as a message bubble with the correct content.

**Validates: Requirements 1.1**

### Property 2: AI Service Model Configuration

*For any* message sent to the AI service, the Groq API should be called with the model parameter set to "llama3-8b-8192".

**Validates: Requirements 1.2**

### Property 3: Typing Indicator During Processing

*For any* chat request, while the AI service is processing, the typing indicator should be visible in the UI.

**Validates: Requirements 1.3**

### Property 4: AI Response Display

*For any* AI response received from the backend, the response should appear in the chat area as a message bubble with the AI content.

**Validates: Requirements 1.4**

### Property 5: Markdown and Code Rendering

*For any* AI response containing markdown or code blocks, the rendered HTML should include proper formatting tags for markdown and syntax highlighting classes for code.

**Validates: Requirements 1.5, 1.6, 11.5**

### Property 6: Enter Key Submission

*For any* non-empty input field state, when the Enter key is pressed (without Shift), the message should be submitted and the input cleared.

**Validates: Requirements 1.7**

### Property 7: Shift+Enter Newline Insertion

*For any* input field state, when Shift+Enter is pressed, a newline character should be inserted without triggering message submission.

**Validates: Requirements 1.8**

### Property 8: Auto-Scroll to Latest Message

*For any* chat state, when a new message is added, the chat container should scroll to show the latest message at the bottom.

**Validates: Requirements 1.9**

### Property 9: Code Mode Analysis

*For any* message in code mode containing code, the AI response should include analysis content (detectable by keywords like "error", "bug", "improve", "suggestion").

**Validates: Requirements 2.2, 11.1**

### Property 10: Exam Mode Question Count

*For any* topic request in exam mode, the AI response should contain exactly 5 questions with corresponding answers.

**Validates: Requirements 2.3, 12.1, 12.2**

### Property 11: Exam Question Formatting

*For any* exam mode response, the questions should be formatted as a numbered list with clear separation between questions and answers.

**Validates: Requirements 12.3, 12.4**

### Property 12: Study Plan Day Count

*For any* subject request in study plan mode, the AI response should contain a 7-day structured plan with content for each day.

**Validates: Requirements 2.4, 13.1, 13.2, 13.3**

### Property 13: Document Mode Context Usage

*For any* question in document mode with selected document context, the AI request should include the document context and the response should reference the provided content.

**Validates: Requirements 2.5, 4.5**

### Property 14: Mode Display in Navbar

*For any* active chat mode, the navbar should display the current mode name.

**Validates: Requirements 2.7**

### Property 15: Mode Selector Update

*For any* mode change action, the mode selector UI should update to reflect the newly selected mode.

**Validates: Requirements 2.8**

### Property 16: PDF Upload Acceptance

*For any* valid PDF file, the upload endpoint should accept the file and return a success response (HTTP 200).

**Validates: Requirements 3.1**

### Property 17: Multi-Page Text Extraction

*For any* multi-page PDF document, the PDF service should extract and return text from all pages that contain extractable text.

**Validates: Requirements 3.2, 15.3, 15.5**

### Property 18: S3 Upload After Extraction

*For any* successfully processed PDF, the S3 service upload method should be called with the file bytes and filename.

**Validates: Requirements 3.3**

### Property 19: Document Summary Generation

*For any* uploaded PDF, the response should include a non-empty summary field generated by the AI service.

**Validates: Requirements 3.4**

### Property 20: Upload Response Metadata

*For any* successful PDF upload, the response should include filename, S3 URL, summary, extracted text, timestamp, and size fields.

**Validates: Requirements 3.5, 5.5**

### Property 21: Document List Update After Upload

*For any* successful document upload, the document should appear in the sidebar documents list.

**Validates: Requirements 3.8**

### Property 22: Document List Load on Page Load

*For any* page load, the documents endpoint should be called and the results should populate the sidebar.

**Validates: Requirements 4.2**

### Property 23: All Documents Displayed

*For any* set of uploaded documents, each document name should appear in the sidebar list.

**Validates: Requirements 4.3**

### Property 24: Document Selection Context Loading

*For any* document selected from the sidebar, the document's extracted text should be loaded as the current context.

**Validates: Requirements 4.4**

### Property 25: Selected Document Visual Indication

*For any* selected document, the document element should have a visual indicator (CSS class or style) distinguishing it from unselected documents.

**Validates: Requirements 4.6**

### Property 26: Chat Endpoint JSON Response

*For any* valid chat request, the /chat endpoint should return a JSON response containing response, mode, and timestamp fields.

**Validates: Requirements 5.3**

### Property 27: Invalid Data Error Response

*For any* endpoint receiving invalid data, the response should be an HTTP error status code (4xx or 5xx) with an error message in the response body.

**Validates: Requirements 5.7**

### Property 28: New Chat Button Clears Messages

*For any* chat state with existing messages, clicking the new chat button should remove all messages from the chat area.

**Validates: Requirements 6.5**

### Property 29: Theme Toggle Switching

*For any* current theme state, clicking the theme toggle should switch to the opposite theme (dark ↔ light).

**Validates: Requirements 7.3**

### Property 30: Theme Persistence Round Trip

*For any* theme selection, after saving to localStorage and reloading the page, the same theme should be applied.

**Validates: Requirements 7.5, 7.6**

### Property 31: Copy Button on AI Messages

*For any* AI response message bubble, a copy button should be present and visible.

**Validates: Requirements 8.1**

### Property 32: Copy to Clipboard Functionality

*For any* message with a copy button, clicking the button should copy the message text to the system clipboard.

**Validates: Requirements 8.2**

### Property 33: Copy Confirmation Feedback

*For any* successful copy action, a visual confirmation indicator should appear temporarily.

**Validates: Requirements 8.3**

### Property 34: Message Bubble Style Differentiation

*For any* pair of user and AI messages, the message bubbles should have different CSS classes or styles to distinguish them visually.

**Validates: Requirements 8.4, 8.5**

### Property 35: Dashboard Statistics Display

*For any* dashboard page load, the page should display total counts for documents, chats, and study plans.

**Validates: Requirements 9.2, 9.3, 9.4, 9.5**

### Property 36: Dashboard Theme Consistency

*For any* theme applied to the chat workspace, the dashboard should use the same theme styling (CSS variables).

**Validates: Requirements 9.6**

### Property 37: Missing Environment Variables Error

*For any* application startup without required environment variables (GROQ_API_KEY, AWS credentials), the application should fail to start or return an error when those services are accessed.

**Validates: Requirements 10.3**

### Property 38: PDF Extraction Error Handling

*For any* valid PDF file, the PDF service should either successfully extract text or return a descriptive error without raising unhandled exceptions.

**Validates: Requirements 15.6**

### Property 39: Empty Message Submission Prevention

*For any* empty or whitespace-only input, the chat workspace should prevent message submission and display a validation message.

**Validates: Requirements 14.4**

### Property 40: Network Error Notification

*For any* failed network request, the chat workspace should display an error notification to the user.

**Validates: Requirements 14.5**

### Property 41: Error State Cleanup

*For any* error occurrence during chat processing, the typing indicator should be removed from the UI.

**Validates: Requirements 14.6**


## Error Handling

### Error Categories and Handling Strategy

#### 1. External API Errors (Groq API)

**Error Types:**
- Network timeout or connection failure
- Invalid API key (401 Unauthorized)
- Rate limiting (429 Too Many Requests)
- Invalid request format (400 Bad Request)
- Service unavailable (503)

**Handling Approach:**
```python
try:
    response = await groq_client.chat.completions.create(...)
except GroqAPIError as e:
    logger.error(f"Groq API error: {e}")
    return {
        "error": "AI service temporarily unavailable. Please try again.",
        "detail": str(e) if app_env == "development" else None
    }
except asyncio.TimeoutError:
    logger.error("Groq API timeout")
    return {
        "error": "Request timed out. Please try again with a shorter message."
    }
```

**User-Facing Messages:**
- Connection errors: "Unable to connect to AI service. Please check your internet connection."
- Rate limiting: "Too many requests. Please wait a moment and try again."
- Invalid API key: "AI service configuration error. Please contact support."

#### 2. AWS S3 Errors

**Error Types:**
- Authentication failure (invalid credentials)
- Bucket not found or access denied
- Network connectivity issues
- Upload size limit exceeded

**Handling Approach:**
```python
try:
    s3_client.upload_fileobj(...)
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'NoSuchBucket':
        logger.error(f"S3 bucket not found: {bucket_name}")
        return {"error": "Storage configuration error. Please contact support."}
    elif error_code == 'AccessDenied':
        logger.error("S3 access denied")
        return {"error": "Storage access error. Please contact support."}
    else:
        logger.error(f"S3 error: {e}")
        return {"error": "Failed to store document. Please try again."}
```

**User-Facing Messages:**
- Upload failures: "Failed to save document. Please try again."
- Access errors: "Storage service unavailable. Please contact support."

#### 3. PDF Processing Errors

**Error Types:**
- Corrupted or invalid PDF file
- Password-protected PDF
- Empty or no extractable text
- Unsupported PDF version

**Handling Approach:**
```python
try:
    reader = PdfReader(BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        try:
            text += page.extract_text() or ""
        except Exception as page_error:
            logger.warning(f"Failed to extract page: {page_error}")
            continue
    
    if not text.strip():
        return {"error": "No text could be extracted from this PDF. It may be an image-based PDF."}
    
    return text
except PdfReadError:
    logger.error("Invalid or corrupted PDF")
    return {"error": "This file appears to be corrupted or is not a valid PDF."}
except Exception as e:
    logger.error(f"PDF processing error: {e}")
    return {"error": "Failed to process PDF. Please try a different file."}
```

**User-Facing Messages:**
- Corrupted files: "This file appears to be corrupted or is not a valid PDF."
- No text: "No text could be extracted. The PDF may contain only images."
- Password-protected: "Password-protected PDFs are not supported."

#### 4. Input Validation Errors

**Error Types:**
- Empty message submission
- Invalid mode selection
- Missing required fields
- File size exceeds limit
- Invalid file type

**Handling Approach:**

Backend validation:
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    if request.mode not in ["chat", "code", "exam", "study_plan", "document"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode: {request.mode}"
        )
    
    if request.mode == "document" and not request.document_context:
        raise HTTPException(
            status_code=400,
            detail="Document context required for document mode"
        )
```

Frontend validation:
```javascript
function validateMessage(message) {
    if (!message || !message.trim()) {
        showNotification("Please enter a message", "warning");
        return false;
    }
    return true;
}

function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        showNotification("File size must be less than 10MB", "error");
        return false;
    }
    if (file.type !== "application/pdf") {
        showNotification("Only PDF files are supported", "error");
        return false;
    }
    return true;
}
```

#### 5. Frontend Network Errors

**Error Types:**
- Network disconnection
- Request timeout
- Server unavailable (502, 503, 504)
- CORS errors

**Handling Approach:**
```javascript
async function sendChatRequest(message, mode) {
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, mode }),
            signal: AbortSignal.timeout(30000) // 30 second timeout
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Request failed");
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === "AbortError") {
            showNotification("Request timed out. Please try again.", "error");
        } else if (error.message.includes("Failed to fetch")) {
            showNotification("Network error. Please check your connection.", "error");
        } else {
            showNotification(error.message, "error");
        }
        throw error;
    } finally {
        hideTypingIndicator();
    }
}
```

### Logging Strategy

**Log Levels:**
- **ERROR**: API failures, service errors, unhandled exceptions
- **WARNING**: Recoverable errors, missing optional data, deprecated usage
- **INFO**: Successful operations, mode changes, document uploads
- **DEBUG**: Request/response details, internal state changes

**Log Format:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('techsaathi.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**What to Log:**
- All API requests to external services (Groq, S3)
- PDF upload and processing events
- Error conditions with stack traces
- User actions (mode changes, document selections) in INFO level
- Performance metrics (response times) in DEBUG level

**What NOT to Log:**
- User message content (privacy)
- API keys or credentials
- Full document text (too verbose)
- Personal information

### Error Response Format

All API errors follow a consistent JSON structure:

```json
{
  "error": "User-friendly error message",
  "detail": "Technical details (development only)",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Frontend displays errors using a notification system with severity levels (info, warning, error, success).

## Testing Strategy

### Dual Testing Approach

This application requires both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit Tests**: Verify specific examples, edge cases, error conditions, and integration points
- **Property-Based Tests**: Verify universal properties across randomized inputs

### Property-Based Testing Configuration

**Library Selection:**
- **Python Backend**: Hypothesis (https://hypothesis.readthedocs.io/)
- **JavaScript Frontend**: fast-check (https://github.com/dubzzz/fast-check)

**Configuration:**
```python
# Python - pytest with hypothesis
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)  # Minimum 100 iterations
@given(message=st.text(min_size=1, max_size=1000))
def test_property_message_display(message):
    """
    Feature: techsaathi-ai-study-copilot, Property 1: Message Display Round Trip
    For any non-empty user message, when submitted to the chat workspace,
    the message should appear in the chat area as a message bubble with the correct content.
    """
    # Test implementation
```

```javascript
// JavaScript - fast-check
import fc from 'fast-check';

fc.assert(
  fc.property(
    fc.string({ minLength: 1, maxLength: 1000 }),
    (message) => {
      /**
       * Feature: techsaathi-ai-study-copilot, Property 1: Message Display Round Trip
       * For any non-empty user message, when submitted to the chat workspace,
       * the message should appear in the chat area as a message bubble with the correct content.
       */
      // Test implementation
    }
  ),
  { numRuns: 100 } // Minimum 100 iterations
);
```

**Property Test Tagging:**
Each property test MUST include a comment tag referencing the design document property:
```
Feature: techsaathi-ai-study-copilot, Property {number}: {property_text}
```

### Test Organization

```
tests/
├── unit/
│   ├── test_ai_service.py          # AI service unit tests
│   ├── test_pdf_service.py         # PDF processing unit tests
│   ├── test_s3_service.py          # S3 operations unit tests
│   └── test_api_endpoints.py       # FastAPI endpoint tests
├── property/
│   ├── test_properties_backend.py  # Backend property tests
│   └── test_properties_frontend.js # Frontend property tests
├── integration/
│   ├── test_upload_flow.py         # End-to-end upload tests
│   └── test_chat_flow.py           # End-to-end chat tests
└── fixtures/
    ├── sample_pdfs/                # Test PDF files
    └── mock_responses.json         # Mock API responses
```

### Unit Test Coverage

**Backend Unit Tests:**

1. **AI Service Tests**
   - Test each mode generates appropriate prompts
   - Test API error handling (mock Groq API failures)
   - Test timeout handling
   - Test invalid mode rejection
   - Example: Test that exam mode with "Python" topic generates 5 questions

2. **PDF Service Tests**
   - Test single-page PDF extraction
   - Test multi-page PDF extraction
   - Test corrupted PDF error handling
   - Test empty PDF handling
   - Test PDF with no extractable text
   - Example: Test specific PDF returns expected text

3. **S3 Service Tests**
   - Test successful upload (mock S3)
   - Test upload failure handling
   - Test document listing
   - Test URL generation
   - Example: Test upload returns valid S3 URL format

4. **API Endpoint Tests**
   - Test each endpoint with valid inputs
   - Test each endpoint with invalid inputs
   - Test authentication/authorization (if added)
   - Test CORS headers
   - Example: Test /chat with empty message returns 400

**Frontend Unit Tests:**

1. **Chat Manager Tests**
   - Test message submission
   - Test message display
   - Test mode switching
   - Test clear chat functionality
   - Example: Test clicking send button adds message to DOM

2. **Upload Manager Tests**
   - Test file validation
   - Test upload success handling
   - Test upload error handling
   - Test document list rendering
   - Example: Test uploading non-PDF shows error

3. **Theme Manager Tests**
   - Test theme toggle
   - Test localStorage persistence
   - Test theme application on load
   - Example: Test toggling from dark to light updates CSS variables

4. **Markdown Renderer Tests**
   - Test basic markdown rendering
   - Test code block rendering
   - Test syntax highlighting application
   - Example: Test "**bold**" renders as `<strong>bold</strong>`

### Property-Based Test Coverage

Each correctness property from the design document should have a corresponding property-based test:

**Backend Property Tests (Examples):**

- **Property 2**: Generate random messages, verify all Groq API calls use "llama3-8b-8192"
- **Property 10**: Generate random topics, verify exam responses contain exactly 5 questions
- **Property 12**: Generate random subjects, verify study plans contain 7 days
- **Property 17**: Generate random multi-page PDFs, verify all pages are processed
- **Property 27**: Generate random invalid inputs, verify all return error responses

**Frontend Property Tests (Examples):**

- **Property 1**: Generate random messages, verify they appear in chat after submission
- **Property 5**: Generate random markdown/code, verify proper HTML rendering
- **Property 30**: Generate random theme selections, verify localStorage round-trip
- **Property 34**: Generate random message pairs, verify different styling

### Integration Tests

**End-to-End Flows:**

1. **Complete Upload Flow**
   - Upload PDF → Extract text → Upload to S3 → Generate summary → Display in sidebar
   - Verify each step completes successfully
   - Verify error handling at each step

2. **Complete Chat Flow**
   - Select mode → Enter message → Submit → Display response
   - Test all 5 modes
   - Verify markdown rendering in responses

3. **Document Q&A Flow**
   - Upload document → Select document → Switch to document mode → Ask question → Verify context used

### Test Data and Fixtures

**Sample PDFs:**
- `simple_text.pdf`: Single page with plain text
- `multi_page.pdf`: 10 pages with varied content
- `empty.pdf`: PDF with no extractable text
- `corrupted.pdf`: Invalid PDF file
- `large.pdf`: PDF near size limit (9.5MB)

**Mock Responses:**
- Groq API success responses for each mode
- Groq API error responses (401, 429, 503)
- S3 success/failure responses

### Testing Commands

```bash
# Run all tests
pytest tests/ --cov=services --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only property tests
pytest tests/property/ -v

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run frontend tests
npm test

# Run frontend property tests
npm run test:property
```

### Continuous Integration

Tests should run automatically on:
- Every commit (unit tests only for speed)
- Every pull request (all tests including property tests)
- Nightly builds (extended property tests with 1000+ iterations)

**CI Configuration (.github/workflows/test.yml):**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=services
```

### Test Maintenance

- Update tests when requirements change
- Add new property tests for new features
- Review and update test data fixtures quarterly
- Monitor test execution time and optimize slow tests
- Maintain minimum 80% code coverage for backend services
- Review property test failures carefully (they often reveal edge cases)

