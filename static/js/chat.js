class ChatManager {
    constructor() {
        this.messages = [];
        this.currentMode = 'chat';
        this.selectedDocument = null;
        this.init();
    }

    init() {
        // Setup event listeners
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        const modeSelector = document.getElementById('modeSelector');
        const newChatBtn = document.getElementById('newChatBtn');

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.handleSend());
        }

        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                // Shift+Enter creates a new line (allow default behavior)
                if (e.key === 'Enter' && e.shiftKey) {
                    return;
                }
                
                // Enter alone sends the message
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleSend();
                }
            });

            // Auto-resize textarea
            messageInput.addEventListener('input', () => {
                messageInput.style.height = 'auto';
                messageInput.style.height = messageInput.scrollHeight + 'px';
            });
        }

        if (modeSelector) {
            modeSelector.addEventListener('change', (e) => {
                this.setMode(e.target.value);
            });
            // Set initial mode
            this.setMode(modeSelector.value);
        }

        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.clearChat());
        }
    }

    async handleSend() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        // Validate message
        if (!message) {
            this.showNotification('Please enter a message', 'warning');
            return;
        }

        // Clear input
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Send message
        await this.sendMessage(message);
    }

    async sendMessage(message) {
        // Add user message to UI
        this.addMessage(message, true);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Prepare request
            const requestBody = {
                message: message,
                mode: this.currentMode
            };

            // Add document context if in document mode
            if (this.currentMode === 'document' && this.selectedDocument) {
                // Limit document context to prevent token overflow (max ~15000 chars = ~4000 tokens)
                const maxContextLength = 15000;
                let context = this.selectedDocument.extracted_text || '';
                
                if (context.length > maxContextLength) {
                    // Take first part of document
                    context = context.substring(0, maxContextLength) + '\n\n[Document truncated for length...]';
                }
                
                requestBody.document_context = context;
            } else if (this.currentMode === 'document' && !this.selectedDocument) {
                throw new Error('Please select a document first for Document Q&A mode');
            }

            // Call API
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Request failed');
            }

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add AI response to UI
            this.addMessage(data.response, false);

        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.showNotification(error.message, 'error');
        }
    }

    addMessage(content, isUser) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        // Remove welcome message if present
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = isUser ? '👤' : '🤖';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';

        if (isUser) {
            messageBubble.textContent = content;
        } else {
            // Render markdown for AI messages
            messageBubble.innerHTML = MarkdownRenderer.render(content);
        }

        messageContent.appendChild(messageBubble);

        // Add copy button for AI messages
        if (!isUser) {
            const messageActions = document.createElement('div');
            messageActions.className = 'message-actions';

            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = '📋 Copy';
            copyBtn.addEventListener('click', () => this.copyToClipboard(content, copyBtn));

            messageActions.appendChild(copyBtn);

            // Add download button if message contains a table
            if (content.includes('|') && content.split('\n').filter(line => line.includes('|')).length > 2) {
                const downloadBtn = document.createElement('button');
                downloadBtn.className = 'copy-btn download-btn';
                downloadBtn.textContent = '📥 Download Table';
                downloadBtn.addEventListener('click', () => this.downloadTable(messageBubble));
                messageActions.appendChild(downloadBtn);
            }

            messageContent.appendChild(messageActions);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        this.scrollToBottom();

        // Store message
        this.messages.push({
            content,
            isUser,
            timestamp: new Date(),
            mode: this.currentMode
        });
    }

    downloadTable(messageBubble) {
        const table = messageBubble.querySelector('table');
        if (!table) {
            this.showNotification('No table found to download', 'error');
            return;
        }

        try {
            // Clone the table to avoid modifying the original
            const tableClone = table.cloneNode(true);
            
            // Create HTML content
            const htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Timetable - TechSaathi AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #4a9eff;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 0 auto;
        }
        th {
            background: linear-gradient(135deg, #4a9eff 0%, #3a7bd5 100%);
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: 600;
        }
        td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f0f7ff;
        }
        td:first-child {
            font-weight: 600;
            background-color: #e3f2fd;
            color: #1976d2;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>📅 My Study Timetable</h1>
    ${tableClone.outerHTML}
    <div class="footer">
        <p>Generated by TechSaathi AI - Your Smart Study Companion</p>
        <p>Date: ${new Date().toLocaleDateString()}</p>
    </div>
</body>
</html>`;

            // Create blob and download
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `timetable-${Date.now()}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.showNotification('Timetable downloaded successfully!', 'success');
        } catch (error) {
            console.error('Download error:', error);
            this.showNotification('Failed to download timetable', 'error');
        }
    }

    async copyToClipboard(text, button) {
        try {
            await navigator.clipboard.writeText(text);
            const originalText = button.textContent;
            button.textContent = '✅ Copied!';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        } catch (error) {
            console.error('Copy error:', error);
            this.showNotification('Failed to copy', 'error');
        }
    }

    showTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    setMode(mode) {
        this.currentMode = mode;
        console.log('Mode changed to:', mode);
        
        // Update mode instructions
        this.updateModeInstructions(mode);
        
        // Update input placeholder based on mode
        this.updateInputPlaceholder(mode);
    }

    updateModeInstructions(mode) {
        // Hide all mode instructions
        const allModeInfos = document.querySelectorAll('.mode-info');
        allModeInfos.forEach(info => {
            info.style.display = 'none';
        });
        
        // Show current mode instruction
        const currentModeInfo = document.querySelector(`.mode-info[data-mode="${mode}"]`);
        if (currentModeInfo) {
            currentModeInfo.style.display = 'block';
        }
    }

    updateInputPlaceholder(mode) {
        const messageInput = document.getElementById('messageInput');
        if (!messageInput) return;
        
        const placeholders = {
            'chat': 'Ask me anything about your studies... (Enter to send, Shift+Enter for new line)',
            'code': 'Paste your code here and describe the issue... (Enter to send, Shift+Enter for new line)',
            'exam': 'Enter a topic (e.g., "Python loops", "World War 2")... (Enter to send, Shift+Enter for new line)',
            'study_plan': 'Enter a subject (e.g., "Machine Learning", "Biology")... (Enter to send, Shift+Enter for new line)',
            'timetable': 'E.g., "Math, Physics, Chemistry - 6 hours daily, 6 AM to 12 PM"... (Enter to send, Shift+Enter for new line)',
            'document': 'Ask a question about the selected document... (Enter to send, Shift+Enter for new line)'
        };
        
        messageInput.placeholder = placeholders[mode] || 'Type your message...';
    }

    setSelectedDocument(doc) {
        this.selectedDocument = doc;
        console.log('Selected document:', doc.filename);
    }

    clearChat() {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        this.messages = [];
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h2>Welcome to TechSaathi AI! <span class="wave-emoji">🤚</span></h2>
                <p>Your smart study companion. Select a mode and start chatting!</p>
            </div>
        `;
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
