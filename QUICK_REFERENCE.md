# TechSaathi AI - Quick Reference Card

## 🚀 Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
uvicorn main:app --reload
```

Open: http://localhost:8000

## 🔑 Required Keys

| Service | Get From | Purpose |
|---------|----------|---------|
| Groq API | https://console.groq.com | AI responses |
| AWS S3 | AWS Console | Document storage |

## 💬 Chat Modes

| Mode | Icon | Purpose | Example |
|------|------|---------|---------|
| Chat | 💬 | General tutoring | "Explain photosynthesis" |
| Code Debug | 💻 | Fix code bugs | Paste your code |
| Exam | 📝 | Practice questions | "Python basics" |
| Study Plan | 📚 | 7-day schedule | "Machine Learning" |
| Document Q&A | 📄 | Ask about PDFs | Upload PDF first |

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Send message |
| Shift + Enter | New line |

## 📁 File Limits

- **Type**: PDF only
- **Size**: Max 10MB
- **Format**: Text-based (not scanned images)

## 🎨 Features

- ✅ Dark/Light theme
- ✅ Markdown support
- ✅ Code highlighting
- ✅ Copy messages
- ✅ Auto-scroll
- ✅ Document upload
- ✅ Statistics dashboard

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Services not initialized | Check .env file |
| Upload fails | Verify AWS credentials |
| No AI response | Check Groq API key |
| Port in use | Change port or kill process |

## 📊 Dashboard Stats

- 📄 Documents uploaded
- 💬 Total chats
- 📚 Study plans created
- 📝 Exams generated
- 💻 Code debugs

## 🌐 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | / | Main interface |
| GET | /dashboard | Statistics |
| POST | /chat | Send message |
| POST | /upload-pdf | Upload file |
| GET | /documents | List files |

## 💡 Tips

### For Best Results

**Code Debugging**
- Include full context
- Mention language
- Describe expected behavior

**Exam Questions**
- Be specific about topic
- Mention difficulty level
- Specify question type

**Study Plans**
- State your current level
- Mention time constraints
- List specific topics

**Document Q&A**
- Use text-based PDFs
- Ask specific questions
- Reference page numbers

## 🎯 Common Use Cases

1. **Homework Help**: Switch to Chat mode
2. **Debug Code**: Switch to Code mode, paste code
3. **Exam Prep**: Switch to Exam mode, specify topic
4. **Study Schedule**: Switch to Study Plan mode
5. **Learn from PDFs**: Upload PDF, switch to Document mode

## 📝 Example Prompts

### Chat Mode
- "Explain the water cycle"
- "What is machine learning?"
- "Help me understand calculus"

### Code Mode
```python
def calculate(a, b):
    return a + b
# Why doesn't this work?
```

### Exam Mode
- "Generate 5 questions on Python loops"
- "Create practice questions for algebra"

### Study Plan Mode
- "Create a 7-day plan for learning React"
- "Study schedule for biology exam"

### Document Mode
- "What is the main argument in chapter 3?"
- "Summarize the key points"

## 🔄 Workflow

1. Select mode from dropdown
2. Type or upload
3. Press Enter or click Send
4. View AI response
5. Copy if needed
6. Continue conversation

## 📱 Interface Layout

```
┌─────────────────────────────────────┐
│  TechSaathi AI  [Mode] [Theme] [📊] │
├──────┬──────────────────────────────┤
│      │                              │
│ 📄   │     Chat Messages            │
│ Docs │                              │
│      │                              │
│ [+]  │                              │
│ [📤] │                              │
├──────┴──────────────────────────────┤
│  Type message... [Send]             │
└─────────────────────────────────────┘
```

## 🎨 Theme Toggle

Click 🌙/☀️ in top-right to switch themes

## 📊 View Stats

Click "📊 Dashboard" in navbar

## 🆕 New Chat

Click "➕ New Chat" in sidebar

## 🔗 Useful Links

- Groq Console: https://console.groq.com
- AWS Console: https://console.aws.amazon.com
- Project Docs: README.md
- Setup Guide: SETUP_GUIDE.md

## ⚡ Performance Tips

- Keep messages concise
- Upload smaller PDFs when possible
- Clear chat periodically
- Use specific modes for specific tasks

## 🛡️ Security Notes

- Never share your .env file
- Keep API keys private
- Don't commit .env to git
- Use strong AWS credentials

## 📞 Getting Help

1. Check logs: `techsaathi.log`
2. Review error messages
3. Verify .env configuration
4. Test API keys separately

---

**Happy Learning! 🎓**
