class UploadManager {
    constructor() {
        this.documents = [];
        this.selectedDocument = null;
        this.init();
    }

    init() {
        // Setup file input listener
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file
        if (!this.validateFile(file)) {
            event.target.value = ''; // Reset input
            return;
        }

        await this.uploadPDF(file);
        event.target.value = ''; // Reset input
    }

    validateFile(file) {
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (file.type !== 'application/pdf') {
            this.showNotification('Only PDF files are supported', 'error');
            return false;
        }
        
        if (file.size > maxSize) {
            this.showNotification('File size must be less than 10MB', 'error');
            return false;
        }
        
        return true;
    }

    async uploadPDF(file) {
        const uploadBtn = document.querySelector('label[for="fileInput"]');
        const originalText = uploadBtn.textContent;
        
        try {
            // Show loading state
            uploadBtn.textContent = '⏳ Uploading...';
            uploadBtn.style.pointerEvents = 'none';
            this.showNotification('Uploading PDF...', 'info');
            console.log('Uploading file:', file.name, 'Size:', file.size);
            
            const startTime = Date.now();
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/upload-pdf', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('Upload failed:', error);
                throw new Error(error.detail || 'Upload failed');
            }

            const data = await response.json();
            const uploadTime = ((Date.now() - startTime) / 1000).toFixed(1);
            console.log('Upload successful:', data);
            
            // Add to documents list
            this.documents.push(data);
            this.renderDocuments();
            
            this.showNotification(`PDF uploaded! (${uploadTime}s)`, 'success');
        } catch (error) {
            console.error('Upload error:', error);
            this.showNotification(error.message, 'error');
        } finally {
            // Restore button state
            uploadBtn.textContent = originalText;
            uploadBtn.style.pointerEvents = 'auto';
        }
    }

    async loadDocuments() {
        try {
            console.log('Loading documents from /documents endpoint...');
            const response = await fetch('/documents');
            
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to load documents:', errorData);
                throw new Error(errorData.detail || 'Failed to load documents');
            }

            const data = await response.json();
            console.log('Documents loaded:', data);
            this.documents = data.documents || [];
            this.renderDocuments();
        } catch (error) {
            console.error('Load documents error:', error);
            this.showNotification('Failed to load documents from storage', 'warning');
        }
    }

    renderDocuments() {
        const documentsList = document.getElementById('documentsList');
        if (!documentsList) return;

        if (this.documents.length === 0) {
            documentsList.innerHTML = '<p style="padding: 1rem; color: var(--text-secondary); text-align: center;">No documents uploaded yet</p>';
            return;
        }

        documentsList.innerHTML = this.documents.map(doc => `
            <div class="document-item ${this.selectedDocument?.filename === doc.filename ? 'selected' : ''}" 
                 data-filename="${doc.filename}"
                 title="${doc.summary || doc.filename}">
                <span class="document-name">📄 ${doc.filename}</span>
                <button class="document-delete-btn" data-filename="${doc.filename}" title="Delete document">×</button>
            </div>
        `).join('');

        // Add click listeners for document selection
        documentsList.querySelectorAll('.document-item').forEach(item => {
            const docName = item.querySelector('.document-name');
            docName.addEventListener('click', () => {
                const filename = item.dataset.filename;
                this.selectDocument(filename);
            });
        });

        // Add click listeners for delete buttons
        documentsList.querySelectorAll('.document-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent document selection
                const filename = btn.dataset.filename;
                this.deleteDocument(filename);
            });
        });
    }

    async deleteDocument(filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }

        try {
            this.showNotification('Deleting document...', 'info');
            
            // Optimistically remove from UI first for faster perceived performance
            const docIndex = this.documents.findIndex(doc => doc.filename === filename);
            if (docIndex !== -1) {
                this.documents.splice(docIndex, 1);
                this.renderDocuments();
            }
            
            // Call backend to delete from S3
            const response = await fetch(`/documents/${encodeURIComponent(filename)}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                // Restore document if delete failed
                await this.loadDocuments();
                throw new Error(error.detail || 'Delete failed');
            }
            
            // Clear selection if deleted document was selected
            if (this.selectedDocument?.filename === filename) {
                this.selectedDocument = null;
                if (window.chatManager) {
                    window.chatManager.setSelectedDocument(null);
                }
            }
            
            this.showNotification(`Deleted: ${filename}`, 'success');
        } catch (error) {
            console.error('Delete error:', error);
            this.showNotification(error.message || 'Failed to delete document', 'error');
        }
    }

    async selectDocument(filename) {
        // Find document
        const doc = this.documents.find(d => d.filename === filename);
        if (!doc) return;

        // If document doesn't have extracted_text, fetch it
        if (!doc.extracted_text) {
            // Show loading notification
            this.showNotification('Loading document...', 'info');
            
            try {
                const response = await fetch(`/documents/${encodeURIComponent(filename)}/content`);
                if (response.ok) {
                    const data = await response.json();
                    doc.extracted_text = data.extracted_text;
                    doc.summary = data.summary;
                } else {
                    throw new Error('Failed to load document');
                }
            } catch (error) {
                console.error('Failed to fetch document content:', error);
                this.showNotification('Failed to load document content', 'error');
                return;
            }
        }

        this.selectedDocument = doc;
        this.renderDocuments();

        // Notify chat manager if available
        if (window.chatManager) {
            window.chatManager.setSelectedDocument(doc);
        }

        this.showNotification(`Selected: ${filename}`, 'success');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        container.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}
