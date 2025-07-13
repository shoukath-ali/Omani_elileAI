"""
Voice-Only Omani Arabic Mental Health Chatbot
Main Mental Health Bot - Therapeutic Logic & Coordination
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from speech_service import transcribe_audio, synthesize_speech, test_speech_services
from ai_service import get_ai_response, clear_conversation_history
from config import settings, EMERGENCY_CONTACTS, ISLAMIC_CBT_TECHNIQUES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OmaniMentalHealthBot:
    """Main mental health chatbot with voice-only interface"""
    
    def __init__(self):
        """Initialize the mental health bot"""
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.conversation_count = 0
        self.crisis_alerts = []
        self.response_times = []
        
        logger.info(f"Omani Mental Health Bot initialized - Session: {self.session_id}")
    
    async def process_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Main processing pipeline: Audio → STT → AI → TTS → Audio
        
        Args:
            audio_data: Raw audio bytes from user
            
        Returns:
            Dict with response audio and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Speech-to-Text
            logger.info("🎤 Processing speech-to-text...")
            stt_result = await transcribe_audio(audio_data)
            
            if not stt_result["success"]:
                return {
                    "success": False,
                    "error": f"Speech recognition failed: {stt_result.get('error', 'Unknown error')}",
                    "stage": "stt"
                }
            
            user_text = stt_result["text"]
            if not user_text.strip():
                # Enhanced error message with audio info
                audio_info = ""
                if "audio_duration" in stt_result:
                    duration = stt_result["audio_duration"]
                    volume = stt_result.get("audio_volume", "unknown")
                    audio_info = f" (Duration: {duration:.1f}s, Volume: {volume:.1f}dBFS)"
                
                error_msg = stt_result.get("error", "No speech detected") + audio_info
                tips = "\n\n💡 Tips:\n• Speak clearly for at least 1 second\n• Move closer to microphone\n• Check if microphone is working\n• Try speaking louder"
                
                return {
                    "success": False,
                    "error": error_msg + tips,
                    "stage": "stt",
                    "audio_info": stt_result
                }
            
            logger.info(f"✅ STT Success: '{user_text[:50]}...'")
            
            # Step 2: AI Processing
            logger.info("🤖 Processing AI response...")
            ai_result = await get_ai_response(user_text, self.session_id)
            
            if not ai_result["success"]:
                return {
                    "success": False,
                    "error": f"AI processing failed: {ai_result.get('error', 'Unknown error')}",
                    "stage": "ai",
                    "user_text": user_text
                }
            
            response_text = ai_result["response"]
            crisis_detected = ai_result.get("crisis_detected", False)
            
            logger.info(f"✅ AI Response: '{response_text[:50]}...'")
            
            # Handle crisis detection
            if crisis_detected:
                self._handle_crisis_detection(user_text, response_text)
                # Enhance response with crisis support
                response_text = self._enhance_crisis_response(response_text)
            
            # Step 3: Text-to-Speech
            logger.info("🔊 Processing text-to-speech...")
            tts_result = await synthesize_speech(response_text, settings.tts_voice_female)
            
            if not tts_result["success"]:
                return {
                    "success": False,
                    "error": f"Speech synthesis failed: {tts_result.get('error', 'Unknown error')}",
                    "stage": "tts",
                    "user_text": user_text,
                    "response_text": response_text
                }
            
            # Calculate total processing time
            total_time = time.time() - start_time
            self.response_times.append(total_time)
            self.conversation_count += 1
            
            logger.info(f"✅ TTS Success - Total processing time: {total_time:.2f}s")
            
            return {
                "success": True,
                "user_text": user_text,
                "response_text": response_text,
                "audio_data": tts_result["audio_data"],
                "crisis_detected": crisis_detected,
                "processing_time": total_time,
                "conversation_count": self.conversation_count,
                "stt_time": stt_result.get("processing_time", 0),
                "ai_time": ai_result.get("processing_time", 0),
                "tts_time": tts_result.get("processing_time", 0)
            }
            
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "stage": "general",
                "processing_time": time.time() - start_time
            }
    
    def _handle_crisis_detection(self, user_text: str, response_text: str):
        """Handle crisis detection and logging"""
        crisis_event = {
            "timestamp": datetime.now(),
            "user_text": user_text,
            "response_text": response_text,
            "session_id": self.session_id
        }
        
        self.crisis_alerts.append(crisis_event)
        logger.warning(f"🚨 CRISIS DETECTED - Session: {self.session_id}")
        
        # In production, this would trigger alerts to supervisors
        if settings.enable_logging:
            logger.info("Crisis event logged for review")
    
    def _enhance_crisis_response(self, response_text: str) -> str:
        """Enhance response with crisis support information"""
        crisis_support = f"""
        
        🚨 في حالة الطوارئ:
        - اتصل بالطوارئ: {EMERGENCY_CONTACTS['police']}
        - الخط الساخن للصحة النفسية: {EMERGENCY_CONTACTS['mental_health_hotline']}
        - وزارة الصحة: {EMERGENCY_CONTACTS['ministry_of_health']}
        
        أنت لست وحدك، والمساعدة متوفرة دائماً.
        """
        
        return response_text + crisis_support
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "session_id": self.session_id,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds(),
            "conversation_count": self.conversation_count,
            "avg_response_time": round(avg_response_time, 2),
            "total_crises_detected": len(self.crisis_alerts),
            "performance_target_met": avg_response_time < settings.max_response_time,
            "session_start": self.session_start_time.isoformat()
        }
    
    def test_system(self) -> Dict[str, Any]:
        """Test all system components"""
        logger.info("🔍 Testing system components...")
        
        results = {
            "speech_services": test_speech_services(),
            "ai_services": self._test_ai_services(),
            "overall_status": "unknown"
        }
        
        # Determine overall status
        speech_ok = results["speech_services"]["whisper_available"] and results["speech_services"]["azure_tts_available"]
        ai_ok = results["ai_services"]["openai_available"] and results["ai_services"]["anthropic_available"]
        
        if speech_ok and ai_ok:
            results["overall_status"] = "healthy"
        elif speech_ok or ai_ok:
            results["overall_status"] = "partial"
        else:
            results["overall_status"] = "error"
        
        logger.info(f"✅ System test completed - Status: {results['overall_status']}")
        return results
    
    def _test_ai_services(self) -> Dict[str, Any]:
        """Test AI service availability"""
        results = {
            "openai_available": False,
            "anthropic_available": False
        }
        
        try:
            # Test OpenAI
            if settings.openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=settings.openai_api_key)
                test_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                results["openai_available"] = True
                logger.info("✅ OpenAI GPT-4o available")
            else:
                logger.warning("⚠️ OpenAI API key not configured")
            
        except Exception as e:
            logger.warning(f"⚠️ OpenAI test failed: {e}")
        
        try:
            # Test Anthropic
            if settings.anthropic_api_key:
                from anthropic import Anthropic
                client = Anthropic(api_key=settings.anthropic_api_key)
                test_response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Test"}]
                )
                results["anthropic_available"] = True
                logger.info("✅ Anthropic Claude available")
            else:
                logger.warning("⚠️ Anthropic API key not configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Anthropic test failed: {e}")
        
        return results
    
    def reset_session(self):
        """Reset session for new conversation"""
        self.session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self.conversation_count = 0
        self.crisis_alerts = []
        self.response_times = []
        
        # Clear AI conversation history
        clear_conversation_history()
        
        logger.info(f"🔄 Session reset - New session: {self.session_id}")
    
    def get_therapeutic_resources(self) -> Dict[str, Any]:
        """Get Islamic CBT resources and techniques"""
        return {
            "techniques": ISLAMIC_CBT_TECHNIQUES,
            "emergency_contacts": EMERGENCY_CONTACTS,
            "cultural_approach": "Gulf Arab Islamic counseling",
            "primary_language": settings.primary_language,
            "therapeutic_model": "CBT + Islamic principles"
        }

# Global bot instance
omani_bot = OmaniMentalHealthBot()

# Convenience functions
async def process_user_voice(audio_data: bytes) -> Dict[str, Any]:
    """Convenience function for processing voice input"""
    return await omani_bot.process_voice_input(audio_data)

def get_bot_stats() -> Dict[str, Any]:
    """Convenience function for getting session stats"""
    return omani_bot.get_session_stats()

def test_bot_system() -> Dict[str, Any]:
    """Convenience function for testing system"""
    return omani_bot.test_system()

def reset_bot_session():
    """Convenience function for resetting session"""
    omani_bot.reset_session() 