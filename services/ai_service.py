from groq import Groq
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI interactions using Groq API"""
    
    # Mode-specific system prompts
    MODE_PROMPTS = {
        'chat': "You are TechSaathi, a helpful AI tutor. Provide clear, educational responses to student questions.",
        'code': "You are a code debugging assistant. Analyze the provided code for syntax errors, logical bugs, and suggest improvements. Explain what the code does and provide corrected versions.",
        'exam': "Generate exactly 5 exam questions on the given topic. Format as:\n\nQuestion 1: [question]\nAnswer: [answer]\n\nQuestion 2: [question]\nAnswer: [answer]\n\n(continue for all 5 questions)",
        'study_plan': "You are a study planning expert. Create a comprehensive 7-day study plan for the given subject. For each day, provide:\n- Specific topics to cover\n- Learning activities\n- Practice exercises\n- Time estimates\n\nFormat your response as:\n\n**Day 1:**\n- Topics: [list topics]\n- Activities: [list activities]\n- Practice: [exercises]\n\n**Day 2:**\n[continue for all 7 days]\n\nMake the plan realistic, progressive, and achievable.",
        'timetable': "You are a timetable creation assistant. Create a personalized weekly study timetable based ONLY on the subjects the user mentions. CRITICAL RULES:\n1. Use ONLY the subjects the user explicitly mentions - DO NOT add any other subjects\n2. ALWAYS format as a markdown table:\n\n| Time | Monday | Tuesday | Wednesday | Thursday | Friday | Saturday | Sunday |\n|------|--------|---------|-----------|----------|--------|----------|--------|\n| 6:00-7:00 | Subject | Subject | Subject | Subject | Subject | Subject | Subject |\n\n3. Distribute ONLY the user's subjects across the week\n4. Include breaks (☕ Break), meals (🍽️ Meal), and rest (😴 Rest) as needed\n5. Use the time range the user specifies\n6. Balance the subjects evenly across days\n7. DO NOT invent or suggest additional subjects",
        'document': "You are TechSaathi, an expert AI tutor helping students learn from their study materials. A student has uploaded a document and needs your help understanding it.\n\nYour role:\n- Carefully read the document content provided\n- Answer the student's question using information from the document\n- Format your response with clear paragraphs and proper spacing\n- Use bullet points or numbered lists when explaining multiple concepts\n- Add line breaks between different sections of your answer\n- Explain concepts in simple, clear language\n- Provide examples when helpful\n- Be encouraging and supportive\n\nFormat your responses professionally with proper spacing, just like a well-structured educational explanation."
    }
    
    VALID_MODES = ['chat', 'code', 'exam', 'study_plan', 'timetable', 'document']
    
    def __init__(self, api_key: str):
        """
        Initialize AI service with Groq API key.
        
        Args:
            api_key: Groq API key
        """
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"  # Updated to current model
        logger.info("AI service initialized with Groq API")
    
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
            ValueError: If mode is invalid or document_context missing for document mode
            Exception: If API request fails
        """
        # Validate mode
        if mode not in self.VALID_MODES:
            logger.error(f"Invalid mode: {mode}")
            raise ValueError(f"Invalid mode: {mode}. Must be one of {self.VALID_MODES}")
        
        # Validate document context for document mode
        if mode == 'document' and not document_context:
            logger.error("Document context required for document mode")
            raise ValueError("Document context required for document mode")
        
        # Build system prompt
        system_prompt = self.MODE_PROMPTS[mode]
        
        # Build user message
        if mode == 'document':
            user_message = f"""DOCUMENT CONTENT:
---
{document_context}
---

STUDENT'S QUESTION: {message}

Please answer the student's question based on the document content above."""
        else:
            user_message = message
        
        try:
            # Call Groq API
            logger.info(f"Generating response for mode: {mode}")
            
            # Run synchronous Groq API call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=2048
                )
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"Successfully generated response ({len(ai_response)} characters)")
            return ai_response
            
        except asyncio.TimeoutError:
            logger.error("Groq API timeout")
            raise Exception("Request timed out. Please try again with a shorter message.")
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            if "401" in str(e) or "unauthorized" in str(e).lower():
                raise Exception("AI service configuration error. Please contact support.")
            elif "429" in str(e) or "rate limit" in str(e).lower():
                raise Exception("Too many requests. Please wait a moment and try again.")
            elif "503" in str(e) or "unavailable" in str(e).lower():
                raise Exception("AI service temporarily unavailable. Please try again.")
            else:
                raise Exception("AI service temporarily unavailable. Please try again.")
