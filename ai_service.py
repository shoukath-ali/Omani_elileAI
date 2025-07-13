"""
Voice-Only Omani Arabic Mental Health Chatbot
AI Service: GPT-4o + Claude Dual Model with Code-Switching Support
"""

import logging
import asyncio
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic

from config import (
    settings, 
    CRISIS_KEYWORDS_AR, 
    CRISIS_KEYWORDS_EN, 
    CRISIS_KEYWORDS_MIXED,
    OMANI_CULTURAL_PHRASES,
    OMANI_CODESWITCHING_PHRASES,
    CODESWITCHING_PATTERNS,
    CODESWITCHING_CBT_TECHNIQUES
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Handles dual-model AI responses with GPT-4o primary and Claude fallback, supporting code-switching"""
    
    def __init__(self):
        """Initialize AI services"""
        self.openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        self.conversation_history: List[Dict[str, str]] = []
    
    async def get_response(self, user_message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Get AI response using dual-model approach with code-switching support
        
        Args:
            user_message: User's input text (may contain code-switching)
            conversation_id: Unique conversation identifier
            
        Returns:
            Dict with response and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Detect crisis first (includes code-switching patterns)
            crisis_detected = self._detect_crisis(user_message)
            
            # Detect code-switching in user message
            is_codeswitching = self._detect_codeswitching(user_message)
            
            # Get primary response from GPT-4o
            primary_response = await self._get_gpt_response(user_message, is_codeswitching)
            
            # Validate/enhance with Claude if needed
            final_response = await self._validate_with_claude(
                user_message, 
                primary_response, 
                crisis_detected,
                is_codeswitching
            )
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": final_response
            })
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                "success": True,
                "response": final_response,
                "crisis_detected": crisis_detected,
                "is_codeswitching": is_codeswitching,
                "processing_time": processing_time,
                "model_used": "gpt-4o + claude-validation-codeswitching"
            }
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            
            # Fallback response
            fallback_response = self._get_fallback_response(user_message)
            
            return {
                "success": False,
                "response": fallback_response,
                "crisis_detected": self._detect_crisis(user_message),
                "is_codeswitching": self._detect_codeswitching(user_message),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "error": str(e),
                "model_used": "fallback-codeswitching"
            }
    
    async def _get_gpt_response(self, user_message: str, is_codeswitching: bool = False) -> str:
        """Get response from GPT-4o with Omani cultural context and code-switching support"""
        
        system_prompt = self._create_system_prompt(is_codeswitching)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(self.conversation_history[-10:])  # Last 10 exchanges
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                timeout=10
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"GPT-4o error: {e}")
            raise
    
    async def _validate_with_claude(self, user_message: str, gpt_response: str, crisis_detected: bool, is_codeswitching: bool = False) -> str:
        """Validate and enhance GPT response with Claude, supporting code-switching"""
        
        codeswitching_context = ""
        if is_codeswitching:
            codeswitching_context = """
            
            IMPORTANT: The user is using code-switching (mixing Arabic and English), which is natural in Gulf Arabic conversation.
            Your response should also naturally incorporate code-switching where appropriate, reflecting how educated Gulf Arabs speak.
            Use English for modern concepts, technical terms, or when it feels natural, while maintaining Arabic for cultural and emotional expressions.
            """
        
        validation_prompt = f"""
        As an expert in Arabic mental health counseling and Omani culture, evaluate this conversation:

        User (may contain code-switching): {user_message}
        AI Response: {gpt_response}
        Crisis Detected: {crisis_detected}
        Code-switching Detected: {is_codeswitching}
        {codeswitching_context}

        Please:
        1. Ensure cultural appropriateness for Omani/Gulf context
        2. Verify therapeutic quality and empathy
        3. Check Islamic sensitivity if relevant
        4. Improve Arabic dialect authenticity
        5. Enhance crisis response if needed
        6. If code-switching detected, respond naturally with appropriate Arabic-English mixing

        Provide the best possible response in Omani Arabic dialect, incorporating Islamic counseling principles where appropriate.
        Keep response under 200 words and maintain warm, supportive tone.
        """
        
        try:
            if not self.anthropic_client:
                logger.warning("Anthropic API key not configured - skipping Claude validation")
                return gpt_response
            
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                temperature=0.6,
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            claude_response = response.content[0].text.strip()
            
            # Use Claude's enhanced response if it's significantly better
            if len(claude_response) > 50 and ("مرحباً" in claude_response or "السلام" in claude_response or "I understand" in claude_response):
                return claude_response
            else:
                return gpt_response
                
        except Exception as e:
            logger.warning(f"Claude validation error: {e}")
            return gpt_response  # Fallback to GPT response
    
    def _create_system_prompt(self, is_codeswitching: bool = False) -> str:
        """Create system prompt for Omani mental health context with code-switching support"""
        
        codeswitching_instructions = ""
        if is_codeswitching:
            codeswitching_instructions = f"""
            
            IMPORTANT - CODE-SWITCHING MODE:
            The user is mixing Arabic and English naturally (code-switching), which is common in Gulf Arabic conversation.
            You should respond in the same natural way, mixing Arabic and English appropriately:
            
            - Use Arabic for: emotions, cultural concepts, religious terms, greetings, comfort expressions
            - Use English for: modern concepts, technical terms, casual phrases where natural
            - Natural mixing examples: {OMANI_CODESWITCHING_PHRASES}
            - Common patterns: {CODESWITCHING_PATTERNS}
            
            Your response should feel natural to a Gulf Arab speaker who switches between Arabic and English.
            """
        
        return f"""
        أنت مساعد نفسي متخصص في الثقافة العمانية والخليجية. تتحدث باللهجة العمانية وتفهم السياق الثقافي والديني للمجتمع العماني.
        
        {codeswitching_instructions}

        إرشادات مهمة:
        1. استخدم اللهجة العمانية الأصيلة في ردودك
        2. اظهر الحساسية للقيم الإسلامية والثقافة الخليجية
        3. قدم المشورة النفسية المناسبة ثقافياً
        4. استخدم تقنيات العلاج السلوكي المعرفي المتوافقة مع القيم الإسلامية
        5. اذكر الدعاء والذكر عند المناسب
        6. احترم الهيكل الأسري والمجتمعي العماني
        7. في حالة الأزمات، أرشد للاتصال بالطوارئ (9999)

        العبارات الثقافية المناسبة:
        - التحية: {OMANI_CULTURAL_PHRASES['greeting']}
        - التشجيع: {OMANI_CULTURAL_PHRASES['encouragement']}
        - المواساة: {OMANI_CULTURAL_PHRASES['comfort']}
        - الدعم الديني: {OMANI_CULTURAL_PHRASES['religious_comfort']}

        تذكر: أنت تقدم الدعم النفسي وليس التشخيص الطبي. أرشد دائماً لطلب المساعدة المهنية عند الحاجة.
        
        حافظ على ردودك قصيرة ومفيدة (أقل من 150 كلمة) لتناسب المحادثة الصوتية.
        """
    
    def _detect_crisis(self, text: str) -> bool:
        """Detect crisis keywords in Arabic, English, and code-switching patterns"""
        text_lower = text.lower()
        
        # Check Arabic crisis keywords
        for keyword in CRISIS_KEYWORDS_AR:
            if keyword in text_lower:
                return True
        
        # Check English crisis keywords
        for keyword in CRISIS_KEYWORDS_EN:
            if keyword in text_lower:
                return True
        
        # Check code-switching crisis patterns
        for keyword in CRISIS_KEYWORDS_MIXED:
            if keyword.lower() in text_lower:
                return True
        
        return False
    
    def _detect_codeswitching(self, text: str) -> bool:
        """Detect if text contains Arabic-English code-switching patterns"""
        if not text:
            return False
        
        # Check if text contains both Arabic and English characters
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        has_english = any(char.isalpha() and ord(char) < 128 for char in text)
        
        # Check for common code-switching patterns
        text_lower = text.lower()
        codeswitching_indicators = 0
        
        for category, patterns in CODESWITCHING_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    codeswitching_indicators += 1
        
        # If we have both scripts or multiple indicators
        is_mixed = (has_arabic and has_english) or codeswitching_indicators >= 2
        
        if is_mixed:
            logger.info(f"🌐 Code-switching detected in AI: AR={has_arabic}, EN={has_english}, indicators={codeswitching_indicators}")
        
        return is_mixed
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Generate fallback response for system errors with code-switching support"""
        is_codeswitching = self._detect_codeswitching(user_message)
        
        if self._detect_crisis(user_message):
            if is_codeswitching:
                return f"""
                {OMANI_CODESWITCHING_PHRASES['comfort_mixed']}
                
                I can feel أنك تمر بوقت صعب وأريدك أن تعرف أنك لست وحدك. 
                في حالة الطوارئ، please call:
                - Emergency: 9999
                - Mental Health Hotline: 24673000
                
                {OMANI_CODESWITCHING_PHRASES['religious_comfort_mixed']}
                """
            else:
                return f"""
                {OMANI_CULTURAL_PHRASES['comfort']}
                
                أشعر بقلقك وأريدك أن تعرف أنك لست وحدك. في حالة الطوارئ، يرجى الاتصال بـ:
                - الطوارئ: 9999
                - الخط الساخن للصحة النفسية: 24673000
                
                {OMANI_CULTURAL_PHRASES['religious_comfort']}
                """
        else:
            if is_codeswitching:
                return f"""
                {OMANI_CODESWITCHING_PHRASES['greeting_mixed']}
                
                Sorry، واجهت مشكلة تقنية صغيرة. {OMANI_CODESWITCHING_PHRASES['encouragement_mixed']}
                
                Can you repeat ما قلته؟ I'm here لأستمع إليك وأساعدك.
                """
            else:
                return f"""
                {OMANI_CULTURAL_PHRASES['greeting']}
                
                أعتذر، واجهت مشكلة تقنية صغيرة. {OMANI_CULTURAL_PHRASES['encouragement']}
                
                هل يمكنك إعادة ما قلته؟ أنا هنا لأستمع إليك وأساعدك.
                """
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")

# Global AI service instance
ai_service = AIService()

# Convenience functions
async def get_ai_response(user_message: str, conversation_id: str) -> Dict[str, Any]:
    """Convenience function for getting AI response"""
    return await ai_service.get_response(user_message, conversation_id)

def clear_conversation_history():
    """Convenience function to clear conversation history"""
    ai_service.clear_conversation() 