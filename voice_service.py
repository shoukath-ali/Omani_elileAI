"""
Omani Mental Health Voice Service
Handles Azure Speech Services for STT/TTS with Omani Arabic support
"""
import os
import asyncio
import logging
import tempfile
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import soundfile as sf
import numpy as np

try:
    import azure.cognitiveservices.speech as speechsdk
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

logger = logging.getLogger(__name__)

class OmaniVoiceService:
    """Azure Speech Services wrapper optimized for Omani Arabic dialect"""
    
    def __init__(self):
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.speech_region = os.getenv('AZURE_SPEECH_REGION', 'eastus')
        self.voice_language = os.getenv('VOICE_LANGUAGE', 'ar-OM')
        self.fallback_language = os.getenv('VOICE_FALLBACK_LANGUAGE', 'ar-SA')
        self.tts_voice_name = os.getenv('TTS_VOICE_NAME', 'ar-OM-AyshaNeural')
        self.max_response_time = int(os.getenv('MAX_RESPONSE_TIME', '20'))
        self.voice_quality = os.getenv('VOICE_QUALITY', 'high')
        
        self.speech_config = None
        self.audio_config = None
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize Azure Speech Services"""
        if not AZURE_AVAILABLE:
            logger.error("Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")
            return False
            
        if not self.speech_key:
            logger.error("Azure Speech Key not found. Please set AZURE_SPEECH_KEY environment variable.")
            return False
            
        try:
            # Configure speech service
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key, 
                region=self.speech_region
            )
            
            # Set voice preferences for Omani Arabic
            self.speech_config.speech_recognition_language = self.voice_language
            self.speech_config.speech_synthesis_voice_name = self.tts_voice_name
            
            # Quality settings
            if self.voice_quality == 'high':
                self.speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio48Khz96KBitRateMonoMp3
                )
            
            # Audio configuration for microphone input
            self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            
            logger.info(f"Voice service initialized for {self.voice_language} with voice {self.tts_voice_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech Services: {e}")
            return False
    
    async def speech_to_text(self, audio_data: Optional[bytes] = None, timeout: int = None) -> Dict[str, Any]:
        """
        Convert speech to text using Azure Speech Services
        
        Args:
            audio_data: Optional audio bytes, if None uses microphone
            timeout: Timeout in seconds, defaults to max_response_time
            
        Returns:
            Dict with 'text', 'confidence', 'language', 'success' keys
        """
        import time
        start_time = time.time()
        
        if not self.speech_config:
            return {"success": False, "error": "Speech service not initialized", "text": ""}
        
        timeout = timeout or self.max_response_time
        
        try:
            # Configure audio input
            if audio_data:
                # Convert audio to proper format for Azure Speech SDK
                wav_audio = self._convert_to_wav_format(audio_data)
                
                # Create temporary audio file with proper WAV format
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(wav_audio)
                    temp_file_path = temp_file.name
                
                audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
            else:
                audio_config = self.audio_config
            
            # Create speech recognizer with explicit language settings
            speech_config_copy = speechsdk.SpeechConfig(
                subscription=self.speech_config.get_property(speechsdk.PropertyId.SpeechServiceConnection_Key),
                region=self.speech_region
            )
            speech_config_copy.speech_recognition_language = self.voice_language
            
            # Add cancellation handling
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config_copy, 
                audio_config=audio_config
            )
            
            # Set timeout and event handlers
            speech_recognizer.session_started.connect(lambda evt: logger.info(f"STT Session started: {evt}"))
            speech_recognizer.session_stopped.connect(lambda evt: logger.info(f"STT Session stopped: {evt}"))
            
            def cancellation_handler(evt):
                logger.error(f"Recognition canceled: {evt}")
                if evt.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {evt.error_details}")
            
            speech_recognizer.canceled.connect(cancellation_handler)
            
            # Perform recognition
            result = speech_recognizer.recognize_once_async().get()
            
            # Clean up temporary file
            if audio_data and 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
            # Process result with detailed error handling
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                processing_time = time.time() - start_time
                return {
                    "success": True,
                    "text": result.text.strip(),
                    "confidence": getattr(result, 'confidence', 0.9),
                    "language": self.voice_language,
                    "processing_time": processing_time  # Actual processing time in seconds
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return {
                    "success": False,
                    "error": "No speech detected in audio",
                    "text": "",
                    "details": str(result.no_match_details) if hasattr(result, 'no_match_details') else "No match"
                }
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                error_msg = f"Recognition canceled: {cancellation_details.reason}"
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation_details.error_details}"
                return {
                    "success": False,
                    "error": error_msg,
                    "text": "",
                    "details": str(cancellation_details)
                }
            else:
                return {
                    "success": False,
                    "error": f"Recognition failed: {result.reason}",
                    "text": "",
                    "details": getattr(result, 'cancellation_details', None)
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Speech recognition timeout after {timeout}s",
                "text": ""
            }
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return {
                "success": False,
                "error": f"STT processing error: {str(e)}",
                "text": ""
            }
    
    def _convert_to_wav_format(self, audio_data: bytes) -> bytes:
        """
        Convert audio data to proper WAV format for Azure Speech SDK
        Expected: 16-bit PCM, 16kHz, mono
        """
        try:
            import io
            import wave
            import struct
            
            # If audio_data is already a proper WAV file, validate and return
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                # Validate WAV file format
                try:
                    wav_buffer = io.BytesIO(audio_data)
                    with wave.open(wav_buffer, 'rb') as wav_file:
                        channels = wav_file.getnchannels()
                        sample_width = wav_file.getsampwidth()
                        frame_rate = wav_file.getframerate()
                        
                        logger.info(f"Input WAV: {channels}ch, {sample_width*8}bit, {frame_rate}Hz")
                        
                        # If it matches our requirements, return as-is
                        if channels == 1 and sample_width == 2 and frame_rate == 16000:
                            return audio_data
                        
                        # Otherwise, we need to convert it
                        frames = wav_file.readframes(wav_file.getnframes())
                        
                        # Convert to target format
                        return self._create_wav_file(frames, frame_rate, channels, sample_width)
                        
                except Exception as wav_error:
                    logger.warning(f"WAV validation failed: {wav_error}")
                    # Fall through to raw conversion
            
            # Check if it might be raw PCM data from streamlit-mic-recorder
            # Common format: 44.1kHz, 16-bit, stereo or mono
            logger.info(f"Converting raw audio data: {len(audio_data)} bytes")
            
            # Try to detect format based on data size and common patterns
            if len(audio_data) > 1000:  # Reasonable audio size
                return self._create_wav_file(audio_data, 44100, 1, 2)  # Assume 44.1kHz mono 16-bit
            else:
                logger.warning("Audio data too small, might be invalid")
                return audio_data
                
        except Exception as e:
            logger.warning(f"Audio conversion failed, using original data: {e}")
            return audio_data
    
    def _create_wav_file(self, pcm_data: bytes, input_rate: int, input_channels: int, input_width: int) -> bytes:
        """Create a proper WAV file with target format (16kHz, mono, 16-bit)"""
        try:
            import io
            import wave
            import numpy as np
            
            # Target format for Azure Speech SDK
            target_rate = 16000
            target_channels = 1
            target_width = 2
            
            # Convert PCM data to numpy array for processing
            if input_width == 1:
                dtype = np.uint8
            elif input_width == 2:
                dtype = np.int16
            elif input_width == 4:
                dtype = np.int32
            else:
                dtype = np.int16  # Default
            
            # Read PCM data as numpy array
            audio_array = np.frombuffer(pcm_data, dtype=dtype)
            
            # Handle stereo to mono conversion
            if input_channels == 2:
                audio_array = audio_array.reshape(-1, 2)
                audio_array = np.mean(audio_array, axis=1).astype(dtype)
            
            # Resample if needed (simple decimation/interpolation)
            if input_rate != target_rate:
                # Simple resampling - for production, use scipy.signal.resample
                ratio = target_rate / input_rate
                new_length = int(len(audio_array) * ratio)
                indices = np.linspace(0, len(audio_array) - 1, new_length)
                audio_array = np.interp(indices, np.arange(len(audio_array)), audio_array).astype(dtype)
            
            # Ensure 16-bit format
            if dtype != np.int16:
                if dtype == np.uint8:
                    audio_array = ((audio_array.astype(np.float32) - 128) * 256).astype(np.int16)
                elif dtype == np.int32:
                    audio_array = (audio_array / 65536).astype(np.int16)
                else:
                    audio_array = audio_array.astype(np.int16)
            
            # Create WAV file
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(target_channels)
                wav_file.setsampwidth(target_width)
                wav_file.setframerate(target_rate)
                wav_file.writeframes(audio_array.tobytes())
            
            wav_buffer.seek(0)
            result = wav_buffer.read()
            logger.info(f"Created WAV: {target_channels}ch, {target_width*8}bit, {target_rate}Hz, {len(result)} bytes")
            return result
            
        except Exception as e:
            logger.error(f"WAV creation failed: {e}")
            # Fallback: create basic WAV header
            return self._create_basic_wav(pcm_data)
    
    def _create_basic_wav(self, pcm_data: bytes) -> bytes:
        """Create a basic WAV file with minimal header"""
        try:
            import io
            import wave
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(pcm_data)
            
            wav_buffer.seek(0)
            return wav_buffer.read()
            
        except Exception as e:
            logger.error(f"Basic WAV creation failed: {e}")
            return pcm_data
    
    async def text_to_speech(self, text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert text to speech using Azure Speech Services
        
        Args:
            text: Text to convert to speech
            voice_name: Optional voice name override
            
        Returns:
            Dict with 'audio_data', 'success', 'processing_time' keys
        """
        import time
        start_time = time.time()
        
        if not self.speech_config:
            return {"success": False, "error": "Speech service not initialized"}
        
        if not text.strip():
            return {"success": False, "error": "Empty text provided"}
        
        try:
            # Create a fresh speech config for TTS to avoid conflicts
            tts_config = speechsdk.SpeechConfig(
                subscription=self.speech_config.get_property(speechsdk.PropertyId.SpeechServiceConnection_Key),
                region=self.speech_region
            )
            
            # Set voice
            current_voice = voice_name or self.tts_voice_name
            tts_config.speech_synthesis_voice_name = current_voice
            
            # Set output format to WAV for better compatibility with STT
            tts_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
            )
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=tts_config,
                audio_config=None  # Return audio data instead of playing
            )
            
            # Add cancellation handler
            def cancellation_handler(evt):
                logger.error(f"TTS canceled: {evt}")
                if evt.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"TTS Error details: {evt.error_details}")
            
            synthesizer.synthesis_canceled.connect(cancellation_handler)
            
            # Add cultural and emotional context for Omani dialect
            enhanced_text = self._enhance_text_for_omani_dialect(text)
            
            # Perform synthesis
            result = synthesizer.speak_text_async(enhanced_text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                processing_time = time.time() - start_time
                return {
                    "success": True,
                    "audio_data": result.audio_data,
                    "processing_time": processing_time,  # Actual processing time in seconds
                    "voice_used": current_voice,
                    "text_length": len(text)
                }
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                error_msg = f"TTS canceled: {cancellation_details.reason}"
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation_details.error_details}"
                return {
                    "success": False,
                    "error": error_msg,
                    "details": str(cancellation_details)
                }
            else:
                return {
                    "success": False,
                    "error": f"TTS failed: {result.reason}",
                    "details": getattr(result, 'cancellation_details', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"TTS Error: {e}")
            return {
                "success": False,
                "error": f"TTS processing error: {str(e)}"
            }
    
    def _enhance_text_for_omani_dialect(self, text: str) -> str:
        """
        Enhance text with Omani Arabic dialect and cultural context
        """
        # Add SSML for better pronunciation of Omani terms
        if not text.startswith('<speak>'):
            # Add prosody for natural Omani speech patterns
            enhanced = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{self.voice_language}">
                <prosody rate="0.9" pitch="medium">
                    {text}
                </prosody>
            </speak>"""
            
            # Cultural enhancements for common Omani expressions
            omani_enhancements = {
                'مرحبا': 'أهلاً وسهلاً',  # More welcoming greeting
                'شكرا': 'مشكور',  # Omani thank you
                'إن شاء الله': '<emphasis level="moderate">إن شاء الله</emphasis>',  # Cultural emphasis
                'الحمد لله': '<emphasis level="moderate">الحمد لله</emphasis>',
                'بارك الله فيك': '<emphasis level="moderate">بارك الله فيك</emphasis>'
            }
            
            for standard, omani in omani_enhancements.items():
                enhanced = enhanced.replace(standard, omani)
            
            return enhanced
        
        return text
    
    def get_available_voices(self) -> Dict[str, list]:
        """Get list of available Arabic voices"""
        if not self.speech_config:
            return {"success": False, "voices": []}
        
        try:
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
            voices_result = synthesizer.get_voices_async().get()
            
            arabic_voices = []
            omani_voices = []
            
            for voice in voices_result.voices:
                if voice.locale.startswith('ar-'):
                    voice_info = {
                        "name": voice.short_name,
                        "display_name": voice.local_name,
                        "locale": voice.locale,
                        "gender": voice.gender.name if hasattr(voice.gender, 'name') else str(voice.gender)
                    }
                    
                    if 'OM' in voice.locale:
                        omani_voices.append(voice_info)
                    else:
                        arabic_voices.append(voice_info)
            
            return {
                "success": True,
                "omani_voices": omani_voices,
                "arabic_voices": arabic_voices,
                "total_count": len(omani_voices) + len(arabic_voices)
            }
            
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return {"success": False, "error": str(e), "voices": []}
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Azure Speech Services connection"""
        if not AZURE_AVAILABLE:
            return {
                "success": False,
                "error": "Azure Speech SDK not available",
                "installed": False
            }
        
        if not self.speech_config:
            return {
                "success": False,
                "error": "Speech service not configured",
                "configured": False
            }
        
        try:
            # Test with a simple TTS call
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
            test_text = "اختبار الاتصال"  # "Connection test" in Arabic
            result = synthesizer.speak_text_async(test_text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return {
                    "success": True,
                    "message": "Azure Speech Services connection successful",
                    "language": self.voice_language,
                    "voice": self.tts_voice_name,
                    "region": self.speech_region
                }
            else:
                return {
                    "success": False,
                    "error": f"Test synthesis failed: {result.reason}",
                    "details": getattr(result, 'cancellation_details', None)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}"
            }


# Global voice service instance
_voice_service = None

def get_voice_service() -> OmaniVoiceService:
    """Get or create the global voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = OmaniVoiceService()
    return _voice_service


# Async helper functions for Streamlit
async def process_speech_input(audio_data: Optional[bytes] = None) -> Dict[str, Any]:
    """Process speech input and return text"""
    voice_service = get_voice_service()
    return await voice_service.speech_to_text(audio_data)


async def generate_speech_output(text: str) -> Dict[str, Any]:
    """Generate speech output from text"""
    voice_service = get_voice_service()
    return await voice_service.text_to_speech(text)


# Synchronous wrapper functions for Streamlit compatibility
def sync_speech_to_text(audio_data: Optional[bytes] = None) -> Dict[str, Any]:
    """Synchronous wrapper for speech_to_text"""
    voice_service = get_voice_service()
    try:
        # Check if we're in an async context
        loop = asyncio.get_running_loop()
        # We're in an async context, create a task
        task = asyncio.create_task(voice_service.speech_to_text(audio_data))
        return asyncio.run_coroutine_threadsafe(task, loop).result()
    except RuntimeError:
        # No running loop, safe to create new one
        return asyncio.run(voice_service.speech_to_text(audio_data))


def sync_text_to_speech(text: str, voice_name: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for text_to_speech"""
    voice_service = get_voice_service()
    try:
        # Check if we're in an async context
        loop = asyncio.get_running_loop()
        # We're in an async context, create a task
        task = asyncio.create_task(voice_service.text_to_speech(text, voice_name))
        return asyncio.run_coroutine_threadsafe(task, loop).result()
    except RuntimeError:
        # No running loop, safe to create new one
        return asyncio.run(voice_service.text_to_speech(text, voice_name))


# Utility function for Streamlit integration
def test_voice_setup() -> Dict[str, Any]:
    """Test voice service setup for debugging"""
    voice_service = get_voice_service()
    return voice_service.test_connection() 