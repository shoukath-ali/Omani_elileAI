"""
Voice-Only Omani Arabic Mental Health Chatbot
AI Service: GPT-4o + Claude Dual Model
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic

from config import settings, CRISIS_KEYWORDS_AR, CRISIS_KEYWORDS_EN, OMANI_CULTURAL_PHRASES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """Handles dual-model AI responses with GPT-4o primary and Claude fallback"""
    
    def __init__(self):
        """Initialize AI services"""
        self.openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        self.conversation_history: List[Dict[str, str]] = []
    
    async def get_response(self, user_message: str, conversation_id: str) -> Dict[str, Any]:
        """
        Get AI response using dual-model approach
        
        Args:
            user_message: User's input text
            conversation_id: Unique conversation identifier
            
        Returns:
            Dict with response and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Detect crisis first
            crisis_detected = self._detect_crisis(user_message)
            
            # Get primary response from GPT-4o
            primary_response = await self._get_gpt_response(user_message)
            
            # Validate/enhance with Claude if needed
            final_response = await self._validate_with_claude(
                user_message, 
                primary_response, 
                crisis_detected
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
                "processing_time": processing_time,
                "model_used": "gpt-4o + claude-validation"
            }
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            
            # Fallback response
            fallback_response = self._get_fallback_response(user_message)
            
            return {
                "success": False,
                "response": fallback_response,
                "crisis_detected": self._detect_crisis(user_message),
                "processing_time": asyncio.get_event_loop().time() - start_time,
                "error": str(e),
                "model_used": "fallback"
            }
    
    async def _get_gpt_response(self, user_message: str) -> str:
        """Get response from GPT-4o with Omani cultural context"""
        
        system_prompt = self._create_system_prompt()
        
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
    
    async def _validate_with_claude(self, user_message: str, gpt_response: str, crisis_detected: bool) -> str:
        """Validate and enhance GPT response with Claude"""
        
        validation_prompt = f"""
        As an expert in Arabic mental health counseling and Omani culture, evaluate this conversation:

        User (in Arabic): {user_message}
        AI Response: {gpt_response}
        Crisis Detected: {crisis_detected}

        Please:
        1. Ensure cultural appropriateness for Omani/Gulf context
        2. Verify therapeutic quality and empathy
        3. Check Islamic sensitivity if relevant
        4. Improve Arabic dialect authenticity
        5. Enhance crisis response if needed

        Provide the best possible response in Omani Arabic dialect, incorporating Islamic counseling principles where appropriate.
        Keep response under 200 words and maintain warm, supportive tone.
        """
        
        try:
            if not self.anthropic_client:
                logger.warning("Anthropic API key not configured - skipping Claude validation")
                return gpt_response
            
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                temperature=0.6,
                messages=[{"role": "user", "content": validation_prompt}]
            )
            
            claude_response = response.content[0].text.strip()
            
            # Use Claude's enhanced response if it's significantly better
            if len(claude_response) > 50 and "مرحباً" in claude_response or "السلام" in claude_response:
                return claude_response
            else:
                return gpt_response
                
        except Exception as e:
            logger.warning(f"Claude validation error: {e}")
            return gpt_response  # Fallback to GPT response
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for Omani mental health context"""
        return f"""
        أنت مساعد نفسي متخصص في الثقافة العمانية والخليجية. تتحدث باللهجة العمانية وتفهم السياق الثقافي والديني للمجتمع العماني.

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
        """Detect crisis keywords in Arabic and English"""
        text_lower = text.lower()
        
        # Check Arabic crisis keywords
        for keyword in CRISIS_KEYWORDS_AR:
            if keyword in text_lower:
                return True
        
        # Check English crisis keywords
        for keyword in CRISIS_KEYWORDS_EN:
            if keyword in text_lower:
                return True
        
        return False
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Generate fallback response for system errors"""
        if self._detect_crisis(user_message):
            return f"""
            {OMANI_CULTURAL_PHRASES['comfort']}
            
            أشعر بقلقك وأريدك أن تعرف أنك لست وحدك. في حالة الطوارئ، يرجى الاتصال بـ:
            - الطوارئ: 9999
            - الخط الساخن للصحة النفسية: 24673000
            
            {OMANI_CULTURAL_PHRASES['religious_comfort']}
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