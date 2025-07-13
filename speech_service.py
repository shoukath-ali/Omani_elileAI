"""
Voice-Only Omani Arabic Mental Health Chatbot
Speech Service: Whisper STT + Azure TTS
"""

import io
import logging
import asyncio
import tempfile
from typing import Dict, Any, Optional
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
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
        Convert speech to text using OpenAI Whisper API
        
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
            
            # Convert audio data to temporary file for API upload
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Process audio with pydub for quality analysis
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
                
                # Audio quality analysis
                duration_ms = len(audio_segment)
                duration_seconds = duration_ms / 1000.0
                avg_volume = audio_segment.dBFS
                
                logger.info(f"🎵 Audio analysis: {duration_seconds:.1f}s, {avg_volume:.1f}dBFS")
                
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
                
                # Check if audio is too quiet
                if avg_volume < -50:
                    logger.warning(f"⚠️ Audio very quiet: {avg_volume:.1f}dBFS - may affect transcription")
                
                # Convert to format optimized for API (16kHz, mono)
                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                
                # Normalize audio volume if too quiet
                if avg_volume < -30:
                    audio_segment = audio_segment.normalize()
                    logger.info("🔊 Audio normalized for better recognition")
                
                audio_segment.export(temp_file.name, format="wav")
                
                # Transcribe using OpenAI Whisper API
                with open(temp_file.name, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ar",  # Arabic
                        response_format="text"
                    )
                
                processing_time = asyncio.get_event_loop().time() - start_time
                transcribed_text = transcript.strip() if isinstance(transcript, str) else transcript.text.strip()
                
                # Enhanced empty text handling - try English if Arabic failed
                if not transcribed_text:
                    logger.info("🔄 Arabic transcription empty, trying English...")
                    with open(temp_file.name, "rb") as audio_file:
                        transcript_en = self.openai_client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="en",  # English
                            response_format="text"
                        )
                    
                    transcribed_text = transcript_en.strip() if isinstance(transcript_en, str) else transcript_en.text.strip()
                    
                    if transcribed_text:
                        logger.info(f"✅ English transcription succeeded: '{transcribed_text[:50]}...'")
                    else:
                        return {
                            "success": False,
                            "error": f"No speech detected - Duration: {duration_seconds:.1f}s, Volume: {avg_volume:.1f}dBFS. Try speaking louder and longer.",
                            "text": "",
                            "processing_time": processing_time,
                            "audio_duration": duration_seconds,
                            "audio_volume": avg_volume,
                            "whisper_info": "Both Arabic and English transcription returned empty"
                        }
                
                return {
                    "success": True,
                    "text": transcribed_text,
                    "language": "ar" if not transcribed_text else "auto-detected",
                    "confidence": 0.95,  # OpenAI Whisper API doesn't provide confidence scores
                    "processing_time": processing_time,
                    "audio_duration": duration_seconds,
                    "audio_volume": avg_volume,
                    "api_used": "openai-whisper-api"
                }
                
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
        """Create SSML for better Arabic pronunciation"""
        return f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-OM">
            <voice name="{voice_name}">
                <prosody rate="0.9" pitch="medium">
                    {text}
                </prosody>
            </voice>
        </speak>
        """
    
    def test_services(self) -> Dict[str, Any]:
        """Test both STT and TTS services"""
        results = {
            "whisper_available": False,
            "azure_tts_available": False,
            "omani_voice_available": False
        }
        
        try:
            # Test Whisper
            if self.whisper_model is not None:
                results["whisper_available"] = True
                logger.info("✅ Whisper STT service available")
            
            # Test Azure TTS
            if self.azure_speech_config is not None:
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