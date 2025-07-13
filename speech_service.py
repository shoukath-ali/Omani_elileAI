"""
Voice-Only Omani Arabic Mental Health Chatbot
Speech Service: Whisper STT + Azure TTS
"""

import io
import logging
import asyncio
import tempfile
import os
from typing import Dict, Any, Optional
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import soundfile as sf

from config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechService:
    """Handles speech-to-text and text-to-speech operations"""
    
    def __init__(self):
        """Initialize speech services"""
        self.openai_client = None
        self.azure_speech_config = None
        self.azure_synthesizer = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize OpenAI Whisper API and Azure Speech services"""
        try:
            # Initialize OpenAI Whisper API
            if settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                logger.info("OpenAI Whisper API client initialized successfully")
            else:
                logger.warning("OpenAI API key not provided - STT will be disabled")
                self.openai_client = None
            
            # Initialize Azure Speech
            if settings.azure_speech_key:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=settings.azure_speech_key,
                    region=settings.azure_speech_region
                )
                
                # Set Omani Arabic voice
                self.azure_speech_config.speech_synthesis_voice_name = settings.tts_voice_female
                logger.info(f"Azure TTS configured with voice: {settings.tts_voice_female}")
            else:
                logger.warning("Azure Speech key not provided - TTS will not be available")
                self.azure_speech_config = None
            
        except Exception as e:
            logger.error(f"Failed to initialize speech services: {e}")
            # Don't raise - allow app to start in demo mode
    
    async def speech_to_text(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Convert speech to text using OpenAI Whisper API with code-switching support
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Dict with transcription results
        """
        try:
            if not self.openai_client:
                return {
                    "success": False,
                    "error": "OpenAI Whisper API not available - API key required",
                    "text": "",
                    "processing_time": 0
                }
            
            start_time = asyncio.get_event_loop().time()
            
            # Create temporary file for API upload
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                try:
                    # Simple audio analysis using soundfile (no FFmpeg required)
                    try:
                        # Try to read audio data for basic analysis
                        with io.BytesIO(audio_data) as audio_buffer:
                            data, sample_rate = sf.read(audio_buffer)
                            
                        # Basic audio analysis
                        duration_seconds = len(data) / sample_rate
                        avg_volume = np.mean(np.abs(data)) if len(data) > 0 else 0
                        
                        logger.info(f"🎵 Audio analysis: {duration_seconds:.1f}s, sample_rate: {sample_rate}Hz")
                        
                        # Check minimum duration
                        if duration_seconds < 0.5:
                            return {
                                "success": False,
                                "error": f"Audio too short ({duration_seconds:.1f}s) - minimum 0.5 seconds required",
                                "text": "",
                                "processing_time": asyncio.get_event_loop().time() - start_time,
                                "audio_duration": duration_seconds,
                                "audio_volume": avg_volume
                            }
                        
                        # Check if audio is too quiet (likely noise or silence)
                        if avg_volume < 0.001:
                            logger.warning(f"⚠️ Audio very quiet: {avg_volume:.4f} - may cause incorrect language detection")
                            return {
                                "success": False,
                                "error": f"Audio too quiet ({avg_volume:.4f}) - please speak louder and closer to microphone",
                                "text": "",
                                "processing_time": asyncio.get_event_loop().time() - start_time,
                                "audio_duration": duration_seconds,
                                "audio_volume": avg_volume
                            }
                        
                        # Check if audio is too long (might contain multiple segments that confuse detection)
                        if duration_seconds > 30:
                            logger.warning(f"⚠️ Audio very long: {duration_seconds:.1f}s - may affect language detection accuracy")
                            
                    except Exception as audio_analysis_error:
                        logger.warning(f"Could not analyze audio: {audio_analysis_error}")
                        # Continue anyway - OpenAI Whisper API can handle various formats
                        duration_seconds = 0
                        avg_volume = 0
                    
                    # Write audio data directly to temporary file
                    temp_file.write(audio_data)
                    temp_file.flush()
                    
                    # Try code-switching aware transcription (auto-detect language)
                    logger.info("🌐 Attempting code-switching transcription...")
                    transcribed_text = ""
                    detected_language = "unknown"
                    
                    try:
                        # First attempt: Auto-detect language for code-switching
                        with open(temp_file.name, "rb") as audio_file:
                            transcript = self.openai_client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                # No language parameter = auto-detect
                                response_format="verbose_json"
                            )
                        
                        transcribed_text = transcript.text.strip()
                        detected_language = transcript.language if hasattr(transcript, 'language') else "auto-detected"
                        
                        # FILTER OUT INCORRECT LANGUAGE DETECTIONS
                        # Only accept Arabic, English, or unknown detections
                        expected_languages = ["ar", "en", "arabic", "english", "auto-detected", "unknown"]
                        
                        if detected_language.lower() not in expected_languages:
                            logger.warning(f"⚠️ Unexpected language detected: {detected_language} - forcing fallback")
                            # Clear the result to force Arabic/English fallback
                            transcribed_text = ""
                            detected_language = f"filtered-out-{detected_language}"
                        elif transcribed_text:
                            # Additional validation: reject very short or nonsensical results
                            if len(transcribed_text.strip()) < 2:
                                logger.warning(f"⚠️ Transcription too short ({len(transcribed_text)} chars) - trying fallback")
                                transcribed_text = ""
                            # Reject common Whisper artifacts/noise patterns
                            elif transcribed_text.strip().lower() in ["uh", "um", "ah", "mm", "hm", ".", "!", "?", " "]:
                                logger.warning(f"⚠️ Transcription appears to be noise/artifact: '{transcribed_text}' - trying fallback")
                                transcribed_text = ""
                            else:
                                logger.info(f"✅ Auto-detect transcription: lang={detected_language}, text='{transcribed_text[:50]}...'")
                        
                    except Exception as auto_error:
                        logger.warning(f"Auto-detect transcription failed: {auto_error}")
                    
                    # If auto-detect failed or empty, try Arabic-focused
                    if not transcribed_text:
                        logger.info("🔄 Trying Arabic-focused transcription...")
                        try:
                            with open(temp_file.name, "rb") as audio_file:
                                transcript = self.openai_client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_file,
                                    language="ar",  # Arabic
                                    response_format="text"
                                )
                            
                            transcribed_text = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
                            detected_language = "ar"
                            
                            if transcribed_text:
                                logger.info(f"✅ Arabic transcription succeeded: '{transcribed_text[:50]}...'")
                        
                        except Exception as ar_error:
                            logger.warning(f"Arabic transcription failed: {ar_error}")
                    
                    # If still empty, try English as final fallback
                    if not transcribed_text:
                        logger.info("🔄 Trying English fallback...")
                        try:
                            with open(temp_file.name, "rb") as audio_file:
                                transcript = self.openai_client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_file,
                                    language="en",  # English
                                    response_format="text"
                                )
                            
                            transcribed_text = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
                            detected_language = "en"
                            
                            if transcribed_text:
                                logger.info(f"✅ English transcription succeeded: '{transcribed_text[:50]}...'")
                        
                        except Exception as en_error:
                            logger.warning(f"English transcription failed: {en_error}")
                    
                    # Final check - if still empty, return error
                    if not transcribed_text:
                        return {
                            "success": False,
                            "error": f"No speech detected in any language - Duration: {duration_seconds:.1f}s, Volume: {avg_volume:.4f}. Try speaking louder and longer.",
                            "text": "",
                            "processing_time": asyncio.get_event_loop().time() - start_time,
                            "audio_duration": duration_seconds,
                            "audio_volume": avg_volume,
                            "whisper_info": "Auto-detect, Arabic, and English transcription all returned empty"
                        }
                    
                    # Detect code-switching patterns
                    is_codeswitching = self._detect_codeswitching(transcribed_text)
                    
                    processing_time = asyncio.get_event_loop().time() - start_time
                    
                    return {
                        "success": True,
                        "text": transcribed_text,
                        "language": detected_language,
                        "is_codeswitching": is_codeswitching,
                        "confidence": 0.95,  # OpenAI Whisper API doesn't provide confidence scores
                        "processing_time": processing_time,
                        "audio_duration": duration_seconds,
                        "audio_volume": avg_volume,
                        "api_used": "openai-whisper-api-codeswitching"
                    }
                
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                
        except Exception as e:
            logger.error(f"OpenAI Whisper API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "processing_time": 0
            }
    
    async def text_to_speech(self, text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech using Azure TTS
        
        Args:
            text: Text to synthesize
            voice_name: Optional voice override
            
        Returns:
            Dict with audio data and metadata
        """
        try:
            if not self.azure_speech_config:
                return {
                    "success": False,
                    "error": "Azure TTS not available - Azure Speech key required",
                    "processing_time": 0
                }
            
            start_time = asyncio.get_event_loop().time()
            
            # Use specified voice or default
            current_voice = voice_name or settings.tts_voice_female
            self.azure_speech_config.speech_synthesis_voice_name = current_voice
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=None  # Return audio data instead of playing
            )
            
            # Create SSML for better pronunciation
            ssml_text = self._create_ssml(text, current_voice)
            
            # Synthesize speech
            result = synthesizer.speak_ssml_async(ssml_text).get()
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return {
                    "success": True,
                    "audio_data": result.audio_data,
                    "voice_name": current_voice,
                    "processing_time": processing_time,
                    "text_length": len(text)
                }
            else:
                error_msg = f"TTS failed: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg += f" - {cancellation.reason}: {cancellation.error_details}"
                
                return {
                    "success": False,
                    "error": error_msg,
                    "processing_time": processing_time
                }
                
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": 0
            }
    
    def _create_ssml(self, text: str, voice_name: str) -> str:
        """Create enhanced SSML for better Arabic pronunciation and code-switching support"""
        
        # Detect if text contains code-switching
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        has_english = any(char.isalpha() and ord(char) < 128 for char in text)
        is_codeswitching = has_arabic and has_english
        
        if is_codeswitching:
            logger.info("🌐 Creating code-switching SSML")
            
            # For code-switching, create enhanced SSML with language switching
            # This helps Azure TTS handle mixed content better
            ssml_text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-OM">
                <voice name="{voice_name}">
                    <prosody rate="0.85" pitch="medium">
                        {self._enhance_codeswitching_ssml(text)}
                    </prosody>
                </voice>
            </speak>
            """
        else:
            # Standard SSML for Arabic-only content
            ssml_text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-OM">
                <voice name="{voice_name}">
                    <prosody rate="0.9" pitch="medium">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
        
        return ssml_text
    
    def _enhance_codeswitching_ssml(self, text: str) -> str:
        """
        Enhance SSML for code-switching text to improve pronunciation
        
        Args:
            text: Mixed Arabic-English text
            
        Returns:
            Enhanced SSML with language tags
        """
        import re
        
        # Common English words/phrases that should be marked
        english_patterns = [
            r'\b(I|you|me|my|your|the|and|or|but|so|very|really|actually|basically|literally)\b',
            r'\b(okay|ok|yeah|yes|no|hello|hi|bye|thank you|thanks|sorry|excuse me)\b',
            r'\b(family|work|job|school|university|hospital|doctor|teacher|student)\b',
            r'\b(happy|sad|angry|tired|stressed|worried|excited|disappointed)\b',
            r'\b(today|tomorrow|yesterday|now|later|morning|afternoon|evening|night)\b',
            r'\b(problem|solution|situation|feeling|emotion|thought|idea|plan)\b'
        ]
        
        enhanced_text = text
        
        # Mark common English words with language tags for better pronunciation
        for pattern in english_patterns:
            enhanced_text = re.sub(
                pattern, 
                lambda m: f'<lang xml:lang="en-US">{m.group()}</lang>',
                enhanced_text,
                flags=re.IGNORECASE
            )
        
        # Add slight pauses around language switches for more natural flow
        enhanced_text = re.sub(
            r'(<lang xml:lang="en-US">.*?</lang>)',
            r'<break time="0.1s"/>\1<break time="0.1s"/>',
            enhanced_text
        )
        
        return enhanced_text
    
    def test_services(self) -> Dict[str, Any]:
        """Test both STT and TTS services"""
        results = {
            "whisper_available": False,
            "azure_tts_available": False,
            "omani_voice_available": False
        }
        
        try:
            # Test Whisper
            if self.openai_client: # Check if OpenAI client is initialized
                results["whisper_available"] = True
                logger.info("✅ Whisper STT service available")
            
            # Test Azure TTS
            if self.azure_speech_config: # Check if Azure config is initialized
                results["azure_tts_available"] = True
                logger.info("✅ Azure TTS service available")
                
                # Test Omani voice specifically
                try:
                    synthesizer = speechsdk.SpeechSynthesizer(
                        speech_config=self.azure_speech_config,
                        audio_config=None
                    )
                    
                    test_ssml = self._create_ssml("مرحبا، هذا اختبار للصوت العماني", settings.tts_voice_female)
                    result = synthesizer.speak_ssml_async(test_ssml).get()
                    
                    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                        results["omani_voice_available"] = True
                        logger.info("✅ Omani Arabic voice available")
                    else:
                        logger.warning(f"⚠️ Omani voice test failed: {result.reason}")
                        
                except Exception as voice_test_error:
                    logger.error(f"❌ Omani voice test error: {voice_test_error}")
            
        except Exception as e:
            logger.error(f"Service test error: {e}")
        
        return results

    def _detect_codeswitching(self, text: str) -> bool:
        """
        Detect if text contains Arabic-English code-switching patterns
        
        Args:
            text: Transcribed text to analyze
            
        Returns:
            Boolean indicating if code-switching is detected
        """
        if not text:
            return False
        
        # Simple heuristic: check if text contains both Arabic and English characters
        has_arabic = any('\u0600' <= char <= '\u06FF' for char in text)
        has_english = any(char.isalpha() and ord(char) < 128 for char in text)
        
        # Additional check for common code-switching patterns
        from config import CODESWITCHING_PATTERNS
        
        text_lower = text.lower()
        codeswitching_indicators = 0
        
        # Check for common code-switching patterns
        for category, patterns in CODESWITCHING_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    codeswitching_indicators += 1
        
        # If we have both Arabic and English, or multiple code-switching indicators
        is_mixed = (has_arabic and has_english) or codeswitching_indicators >= 2
        
        if is_mixed:
            logger.info(f"🌐 Code-switching detected: AR={has_arabic}, EN={has_english}, indicators={codeswitching_indicators}")
        
        return is_mixed

# Global speech service instance
speech_service = SpeechService()

# Async convenience functions
async def transcribe_audio(audio_data: bytes) -> Dict[str, Any]:
    """Convenience function for speech-to-text"""
    return await speech_service.speech_to_text(audio_data)

async def synthesize_speech(text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function for text-to-speech"""
    return await speech_service.text_to_speech(text, voice_name)

def test_speech_services() -> Dict[str, Any]:
    """Convenience function to test speech services"""
    return speech_service.test_services() 