# Implementation Plan: TechSaathi AI – Smart Study Copilot

## Overview

This implementation plan breaks down the development of TechSaathi AI Study Copilot into discrete, actionable coding tasks. The application uses FastAPI for the backend, vanilla JavaScript for the frontend, Groq's LLaMA 3 for AI capabilities, AWS S3 for document storage, and pypdf for PDF text extraction. Tasks are organized to build incrementally, with early validation through testing and checkpoints.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure (services/, templates/, static/css/, static/js/)
  - Create requirements.txt with FastAPI, uvicorn, groq, boto3, pypdf, python-dotenv, python-multipart
  - Create .env.example with placeholders for GROQ_API_KEY, AWS credentials, and S3 bucket name
  - Create main.py with basic FastAPI app initialization
  - _Requirements: 10.1, 10.2, 10.3, 10.6, 10.7_

- [ ] 2. Implement S3 service for document storage
  - [x] 2.1 Create S3Service class in services/s3_service.py
    - Implement __init__ method with boto3 client initialization
    - Implement upload_file method to upload files to S3 and return public URL
    - Implement list_documents method to retrieve all documents from S3 bucket
    - Implement get_document_url method to generate document URLs
    - _Requirements: 3.3, 4.1_
  
  - [ ]* 2.2 Write property test for S3 upload
    - **Property 18: S3 Upload After Extraction**
    - **Validates: Requirements 3.3**
  
  - [ ]* 2.3 Write unit tests for S3Service
    - Test successful upload with mocked boto3 client
    - Test upload failure handling (access denied, bucket not found)
    - Test document listing with multiple files
    - Test URL generation format
    - _Requirements: 3.3, 4.1_

- [ ] 3. Implement PDF service for text extraction
  - [x] 3.1 Create PDFService class in services/pdf_service.py
    - Implement extract_text static method using pypdf.PdfReader
    - Implement _extract_page_text helper method with error handling
    - Handle corrupted PDFs, empty pages, and extraction errors
    - _Requirements: 3.2, 3.6, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_
  
  - [ ]* 3.2 Write property test for multi-page PDF extraction
    - **Property 17: Multi-Page Text Extraction**
    - **Validates: Requirements 3.2, 15.3, 15.5**
  
  - [ ]* 3.3 Write unit tests for PDFService
    - Test single-page PDF extraction
    - Test multi-page PDF extraction
    - Test corrupted PDF error handling
    - Test empty PDF handling
    - Test PDF with no extractable text
    - _Requirements: 3.2, 3.6, 15.6_

- [ ] 4. Implement AI service for Groq API integration
  - [x] 4.1 Create AIService class in services/ai_service.py
    - Implement __init__ method with Groq client initialization
    - Implement generate_response async method with mode parameter
    - Implement mode-specific prompt engineering for chat, code, exam, study_plan, document modes
    - Add error handling for API failures, timeouts, and invalid modes
    - _Requirements: 1.2, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 13.1_
  
  - [ ]* 4.2 Write property test for model configuration
    - **Property 2: AI Service Model Configuration**
    - **Validates: Requirements 1.2**
  
  - [ ]* 4.3 Write property test for exam mode question count
    - **Property 10: Exam Mode Question Count**
    - **Validates: Requirements 2.3, 12.1, 12.2**
  
  - [ ]* 4.4 Write property test for study plan day count
    - **Property 12: Study Plan Day Count**
    - **Validates: Requirements 2.4, 13.1, 13.2, 13.3**
  
  - [ ]* 4.5 Write unit tests for AIService
    - Test each mode generates appropriate prompts
    - Test API error handling with mocked Groq API failures
    - Test timeout handling
    - Test invalid mode rejection
    - Test exam mode generates 5 questions
    - Test study plan mode generates 7-day plan
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 5. Checkpoint - Ensure all service tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement FastAPI endpoints
  - [x] 6.1 Create GET "/" endpoint in main.py
    - Serve index.html template using Jinja2Templates
    - _Requirements: 5.1_
  
  - [x] 6.2 Create POST "/chat" endpoint in main.py
    - Define ChatRequest Pydantic model with message, mode, and optional document_context fields
    - Validate message is non-empty and mode is valid
    - Call AIService.generate_response with message, mode, and document_context
    - Return ChatResponse with response, mode, and timestamp
    - Add error handling for empty messages and invalid modes
    - _Requirements: 5.2, 5.3, 14.4_
  
  - [x] 6.3 Create POST "/upload-pdf" endpoint in main.py
    - Accept multipart form data with file field
    - Validate file type is PDF and size is under 10MB
    - Call PDFService.extract_text to get document text
    - Call S3Service.upload_file to store PDF
    - Call AIService.generate_response to create document summary
    - Return upload response with filename, S3 URL, summary, extracted text, timestamp, and size
    - Add error handling for invalid files and processing failures
    - _Requirements: 3.1, 3.4, 3.5, 5.4, 5.5_
  
  - [x] 6.4 Create GET "/documents" endpoint in main.py
    - Call S3Service.list_documents to retrieve all documents
    - Return JSON array of document metadata
    - _Requirements: 4.1, 5.6_
  
  - [x] 6.5 Create GET "/dashboard" endpoint in main.py
    - Serve dashboard.html template
    - Calculate statistics (document count, chat count, etc.)
    - Pass statistics to template
    - _Requirements: 9.1, 9.5_
  
  - [ ]* 6.6 Write property test for invalid data error responses
    - **Property 27: Invalid Data Error Response**
    - **Validates: Requirements 5.7**
  
  - [ ]* 6.7 Write unit tests for API endpoints
    - Test each endpoint with valid inputs
    - Test each endpoint with invalid inputs
    - Test /chat with empty message returns 400
    - Test /upload-pdf with non-PDF returns error
    - Test CORS headers are present
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 7. Configure FastAPI application
  - [ ] 7.1 Add CORS middleware in main.py
    - Configure CORS to allow frontend requests
    - _Requirements: 5.1_
  
  - [ ] 7.2 Add static file mounting in main.py
    - Mount /static directory for CSS and JS files
    - _Requirements: 10.7_
  
  - [ ] 7.3 Add error handling middleware in main.py
    - Implement global exception handler
    - Return consistent error response format
    - Log errors appropriately
    - _Requirements: 14.1, 14.2, 14.3, 14.6_
  
  - [ ] 7.4 Add environment variable loading in main.py
    - Load .env file using python-dotenv
    - Validate required environment variables are present
    - _Requirements: 10.3_

- [ ] 8. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Create HTML templates
  - [x] 9.1 Create templates/index.html for main chat interface
    - Add top navbar with app name, mode selector dropdown, and theme toggle button
    - Add left sidebar with documents list, upload button, and new chat button
    - Add main chat area with message container
    - Add bottom input area with textarea, send button, and attach file button
    - Add typing indicator element (hidden by default)
    - Include links to marked.js and highlight.js libraries
    - Include links to custom CSS and JS files
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 9.2 Create templates/dashboard.html for statistics page
    - Add navigation back to main chat
    - Add statistics display sections for documents, chats, study plans
    - Use same navbar and theme structure as index.html
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.6_

- [ ] 10. Implement CSS styling
  - [x] 10.1 Create static/css/style.css with base styles
    - Define CSS variables for dark theme colors
    - Define CSS variables for light theme colors
    - Add body, navbar, sidebar, and chat area layout styles
    - Add message bubble styles with different colors for user and AI
    - Add input area and button styles
    - Add responsive design media queries
    - Add smooth transitions for theme changes
    - Add rounded corners and modern UI styling
    - _Requirements: 6.6, 6.7, 6.8, 7.1, 7.2, 8.4, 8.5_

- [ ] 11. Implement chat interaction JavaScript
  - [x] 11.1 Create static/js/chat.js with ChatManager class
    - Implement constructor to initialize state (messages array, currentMode, selectedDocument)
    - Implement sendMessage method to submit user messages to /chat endpoint
    - Implement addMessage method to create and display message bubbles
    - Implement showTypingIndicator and hideTypingIndicator methods
    - Implement setMode method to update current mode
    - Implement clearChat method to remove all messages
    - Add event listeners for send button, Enter key, and Shift+Enter
    - Add auto-scroll to latest message functionality
    - Add empty message validation
    - Add network error handling
    - _Requirements: 1.1, 1.3, 1.4, 1.7, 1.8, 1.9, 2.7, 2.8, 6.5, 14.4, 14.5, 14.6_
  
  - [ ]* 11.2 Write property test for message display round trip
    - **Property 1: Message Display Round Trip**
    - **Validates: Requirements 1.1**
  
  - [ ]* 11.3 Write property test for typing indicator
    - **Property 3: Typing Indicator During Processing**
    - **Validates: Requirements 1.3**
  
  - [ ]* 11.4 Write property test for Enter key submission
    - **Property 6: Enter Key Submission**
    - **Validates: Requirements 1.7**
  
  - [ ]* 11.5 Write property test for empty message prevention
    - **Property 39: Empty Message Submission Prevention**
    - **Validates: Requirements 14.4**
  
  - [ ]* 11.6 Write unit tests for ChatManager
    - Test message submission adds message to DOM
    - Test mode switching updates UI
    - Test clear chat removes all messages
    - Test Enter key triggers submission
    - Test Shift+Enter adds newline
    - _Requirements: 1.1, 1.7, 1.8, 6.5_

- [ ] 12. Implement markdown rendering JavaScript
  - [x] 12.1 Create static/js/markdown.js with MarkdownRenderer class
    - Implement static render method using marked.js library
    - Implement static highlightCode method using highlight.js library
    - Configure marked.js to apply syntax highlighting to code blocks
    - _Requirements: 1.5, 1.6, 11.5_
  
  - [ ]* 12.2 Write property test for markdown and code rendering
    - **Property 5: Markdown and Code Rendering**
    - **Validates: Requirements 1.5, 1.6, 11.5**
  
  - [ ]* 12.3 Write unit tests for MarkdownRenderer
    - Test basic markdown rendering (bold, italic, lists)
    - Test code block rendering with language specification
    - Test syntax highlighting is applied
    - _Requirements: 1.5, 1.6_

- [ ] 13. Implement file upload JavaScript
  - [x] 13.1 Create static/js/upload.js with UploadManager class
    - Implement constructor to initialize documents array
    - Implement uploadPDF method to validate and upload files to /upload-pdf endpoint
    - Implement loadDocuments method to fetch from /documents endpoint
    - Implement selectDocument method to highlight and load document context
    - Add file type and size validation (PDF only, max 10MB)
    - Add success/error notification display
    - Add event listeners for upload button and file input
    - _Requirements: 3.1, 3.7, 3.8, 4.2, 4.3, 4.4, 4.6_
  
  - [ ]* 13.2 Write property test for PDF upload acceptance
    - **Property 16: PDF Upload Acceptance**
    - **Validates: Requirements 3.1**
  
  - [ ]* 13.3 Write property test for document list update
    - **Property 21: Document List Update After Upload**
    - **Validates: Requirements 3.8**
  
  - [ ]* 13.4 Write unit tests for UploadManager
    - Test file validation rejects non-PDF files
    - Test file validation rejects files over 10MB
    - Test successful upload updates document list
    - Test document selection loads context
    - _Requirements: 3.1, 3.8, 4.4_

- [ ] 14. Implement theme management JavaScript
  - [x] 14.1 Create static/js/theme.js with ThemeManager class
    - Implement constructor to load theme from localStorage
    - Implement toggleTheme method to switch between dark and light
    - Implement loadTheme method to read from localStorage
    - Implement applyTheme method to set CSS custom properties
    - Add event listener for theme toggle button
    - Add smooth transition animations
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_
  
  - [ ]* 14.2 Write property test for theme persistence
    - **Property 30: Theme Persistence Round Trip**
    - **Validates: Requirements 7.5, 7.6**
  
  - [ ]* 14.3 Write unit tests for ThemeManager
    - Test theme toggle switches between dark and light
    - Test theme is saved to localStorage
    - Test theme is loaded on page load
    - Test CSS variables are updated
    - _Requirements: 7.3, 7.5, 7.6_

- [ ] 15. Implement message interaction features
  - [ ] 15.1 Add copy button functionality to chat.js
    - Add copy button to each AI message bubble
    - Implement copyToClipboard method using navigator.clipboard API
    - Add visual confirmation feedback (tooltip or notification)
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [ ]* 15.2 Write property test for copy functionality
    - **Property 32: Copy to Clipboard Functionality**
    - **Validates: Requirements 8.2**
  
  - [ ]* 15.3 Write unit tests for copy functionality
    - Test copy button is present on AI messages
    - Test clicking copy button copies text
    - Test confirmation feedback is displayed
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 16. Checkpoint - Ensure frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Implement dashboard statistics
  - [ ] 17.1 Add statistics calculation in main.py
    - Count total documents from S3Service
    - Track chat interactions (in-memory counter or from logs)
    - Track study plans generated (in-memory counter)
    - Track exams generated (in-memory counter)
    - Track code debugs (in-memory counter)
    - _Requirements: 9.2, 9.3, 9.4, 9.5_
  
  - [ ] 17.2 Create dashboard JavaScript in static/js/dashboard.js
    - Fetch statistics from backend
    - Display statistics in dashboard UI
    - Apply current theme to dashboard
    - _Requirements: 9.5, 9.6_
  
  - [ ]* 17.3 Write property test for dashboard statistics display
    - **Property 35: Dashboard Statistics Display**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5**

- [ ] 18. Implement comprehensive error handling
  - [ ] 18.1 Add Groq API error handling in ai_service.py
    - Handle network timeouts
    - Handle invalid API key (401)
    - Handle rate limiting (429)
    - Handle service unavailable (503)
    - Return user-friendly error messages
    - _Requirements: 14.1_
  
  - [ ] 18.2 Add S3 error handling in s3_service.py
    - Handle authentication failures
    - Handle bucket not found
    - Handle access denied
    - Return user-friendly error messages
    - _Requirements: 14.2_
  
  - [ ] 18.3 Add PDF processing error handling in pdf_service.py
    - Handle corrupted PDFs
    - Handle password-protected PDFs
    - Handle empty PDFs
    - Return descriptive error messages
    - _Requirements: 14.3_
  
  - [ ] 18.4 Add frontend error notifications in chat.js
    - Display error notifications for network failures
    - Display error notifications for validation failures
    - Remove typing indicator on errors
    - _Requirements: 14.5, 14.6_
  
  - [ ]* 18.5 Write property test for network error notification
    - **Property 40: Network Error Notification**
    - **Validates: Requirements 14.5**
  
  - [ ]* 18.6 Write property test for error state cleanup
    - **Property 41: Error State Cleanup**
    - **Validates: Requirements 14.6**

- [ ] 19. Add logging configuration
  - [ ] 19.1 Configure logging in main.py
    - Set up logging format with timestamp, level, and message
    - Add file handler for techsaathi.log
    - Add console handler for development
    - Log all API requests to external services
    - Log PDF upload and processing events
    - Log error conditions with stack traces
    - Avoid logging sensitive data (API keys, user messages)
    - _Requirements: 14.1, 14.2, 14.3_

- [ ] 20. Integration and wiring
  - [ ] 20.1 Wire all components together in main.py
    - Initialize all services with environment variables
    - Connect endpoints to services
    - Ensure proper error propagation
    - Test end-to-end flows manually
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 5.2, 5.4, 5.6_
  
  - [ ] 20.2 Initialize frontend components in index.html
    - Initialize ChatManager on page load
    - Initialize UploadManager on page load
    - Initialize ThemeManager on page load
    - Connect all event listeners
    - Load initial documents list
    - Apply saved theme
    - _Requirements: 4.2, 7.6_
  
  - [ ]* 20.3 Write integration tests for complete flows
    - Test complete upload flow (upload → extract → S3 → summary → display)
    - Test complete chat flow (select mode → enter message → submit → display response)
    - Test document Q&A flow (upload → select → document mode → ask question)
    - _Requirements: 1.1, 2.5, 3.1, 3.2, 3.3, 3.4, 3.8, 4.4, 4.5_

- [ ] 21. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 22. Create documentation and deployment files
  - [x] 22.1 Create README.md with setup instructions
    - Document prerequisites (Python 3.11+, AWS account, Groq API key)
    - Document installation steps
    - Document environment variable configuration
    - Document how to run the application
    - Document project structure
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 22.2 Verify .env.example is complete
    - Ensure all required environment variables are documented
    - Add comments explaining each variable
    - _Requirements: 10.2, 10.3_
  
  - [ ] 22.3 Create test fixtures directory
    - Add sample PDF files for testing (simple_text.pdf, multi_page.pdf, empty.pdf)
    - Add mock API response JSON files
    - _Requirements: 15.1, 15.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The application uses Python 3.11+ for backend and ES6+ JavaScript for frontend
- All services should be initialized with proper error handling for missing environment variables
- Frontend uses vanilla JavaScript with no framework dependencies except marked.js and highlight.js
