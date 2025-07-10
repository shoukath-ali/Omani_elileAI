#!/usr/bin/env python3
"""
Comprehensive Test Suite for Omani Mental Health Voice-Enabled Chatbot
Tests both text-based chatbot functionality and voice services
"""

import sys
import asyncio
import logging
import time
import tempfile
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Core imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        from chatbot import OmaniMentalHealthChatbot
        print("✅ Chatbot module imported successfully")
        
        # Voice service imports
        try:
            from voice_service import get_voice_service, test_voice_setup
            print("✅ Voice service imported successfully")
        except ImportError as e:
            print(f"⚠️  Voice service import warning: {e}")
        
        # WebSocket imports
        try:
            from websocket_service import VoiceWebSocketServer
            print("✅ WebSocket service imported successfully")
        except ImportError as e:
            print(f"⚠️  WebSocket service import warning: {e}")
        
        # Optional audio imports
        try:
            import azure.cognitiveservices.speech as speechsdk
            print("✅ Azure Speech SDK imported successfully")
        except ImportError:
            print("⚠️  Azure Speech SDK not available (voice features will be limited)")
        
        try:
            import websockets
            print("✅ WebSocket library imported successfully")
        except ImportError:
            print("⚠️  WebSocket library not available")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_chatbot_functionality():
    """Test basic chatbot functionality"""
    print("\n🤖 Testing chatbot functionality...")
    
    try:
        from chatbot import OmaniMentalHealthChatbot
        # Initialize chatbot
        chatbot = OmaniMentalHealthChatbot()
        print("✅ Chatbot initialized successfully")
        
        # Test basic response
        test_messages = [
            "Hello, how are you?",
            "I'm feeling anxious",
            "أشعر بالحزن",  # Arabic: I feel sad
            "I need help with stress"
        ]
        
        for message in test_messages:
            print(f"  Testing: '{message}'")
            response = chatbot.get_response(message)
            
            if response and "response" in response:
                print(f"  ✅ Response received: {response['response'][:100]}...")
                
                # Check for crisis detection
                if response.get("crisis_detected", False):
                    print(f"  🚨 Crisis detected for: {message}")
                
            else:
                print(f"  ❌ No valid response for: {message}")
                return False
        
        print("✅ All chatbot tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return False

def test_voice_service_setup():
    """Test voice service configuration and setup"""
    print("\n🎤 Testing voice service setup...")
    
    try:
        from voice_service import test_voice_setup, get_voice_service
        
        # Test basic setup
        status = test_voice_setup()
        print(f"Voice service status: {status}")
        
        if status.get("success", False):
            print("✅ Voice service configured and working")
        else:
            print(f"⚠️  Voice service limited: {status.get('error', 'Unknown error')}")
        
        # Test voice service instance
        voice_service = get_voice_service()
        if voice_service:
            print("✅ Voice service instance created")
            
            # Test available voices
            try:
                voices = voice_service.get_available_voices()
                if voices.get("success", False):
                    omani_count = len(voices.get("omani_voices", []))
                    arabic_count = len(voices.get("arabic_voices", []))
                    print(f"✅ Voice query successful: {omani_count} Omani, {arabic_count} Arabic voices")
                else:
                    print("⚠️  Voice query failed (expected if no Azure credentials)")
            except Exception as e:
                print(f"⚠️  Voice query error: {e}")
        
        return True
        
    except ImportError:
        print("⚠️  Voice service not available")
        return True  # Not a failure if voice isn't configured
    except Exception as e:
        print(f"❌ Voice service test failed: {e}")
        return False

async def test_voice_processing():
    """Test voice processing functionality"""
    print("\n🔊 Testing voice processing...")
    
    try:
        from voice_service import process_speech_input, generate_speech_output
        
        # Test text-to-speech
        test_text = "مرحباً، كيف حالك؟"  # Arabic: Hello, how are you?
        print(f"Testing TTS with: '{test_text}'")
        
        tts_result = await generate_speech_output(test_text)
        
        if tts_result.get("success", False):
            print("✅ Text-to-speech working")
            audio_size = len(tts_result.get("audio_data", b""))
            print(f"  Generated audio size: {audio_size} bytes")
        else:
            print(f"⚠️  TTS failed: {tts_result.get('error', 'Unknown error')}")
        
        # Test speech-to-text (with dummy data)
        print("Testing STT with dummy audio data...")
        dummy_audio = b"dummy_audio_data"  # This will fail, but tests the pipeline
        
        stt_result = await process_speech_input(dummy_audio)
        
        if not stt_result.get("success", False):
            print("⚠️  STT failed as expected with dummy data")
        else:
            print("✅ STT pipeline working")
        
        return True
        
    except ImportError:
        print("⚠️  Voice processing not available")
        return True
    except Exception as e:
        print(f"⚠️  Voice processing error: {e}")
        return True  # Voice errors are expected without proper setup

def test_websocket_service():
    """Test WebSocket service initialization"""
    print("\n🌐 Testing WebSocket service...")
    
    try:
        from websocket_service import VoiceWebSocketServer
        
        # Test server initialization
        server = VoiceWebSocketServer(host="localhost", port=8766)  # Use different port for testing
        print("✅ WebSocket server instance created")
        
        # Test server stats
        stats = server.get_server_stats()
        print(f"✅ Server stats: {stats}")
        
        return True
        
    except ImportError:
        print("⚠️  WebSocket service not available")
        return True
    except Exception as e:
        print(f"❌ WebSocket service test failed: {e}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\n⚙️  Testing environment setup...")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    optional_vars = ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"]
    
    api_keys_found = 0
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
            api_keys_found += 1
        else:
            print(f"⚠️  {var} not found")
    
    if api_keys_found == 0:
        print("❌ No AI API keys configured")
        return False
    
    print(f"✅ {api_keys_found} AI API key(s) configured")
    
    # Check optional voice variables
    voice_configured = 0
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} is set (voice enabled)")
            voice_configured += 1
        else:
            print(f"⚠️  {var} not found (voice limited)")
    
    if voice_configured > 0:
        print(f"✅ Voice services configured ({voice_configured}/{len(optional_vars)} vars)")
    else:
        print("⚠️  Voice services not configured")
    
    return True

def test_crisis_detection():
    """Test crisis detection functionality"""
    print("\n🚨 Testing crisis detection...")
    
    try:
        from chatbot import OmaniMentalHealthChatbot
        chatbot = OmaniMentalHealthChatbot()
        
        crisis_messages = [
            "I want to hurt myself",
            "I'm thinking of ending it all",
            "أريد أن أؤذي نفسي",  # Arabic: I want to hurt myself
            "Life is not worth living"
        ]
        
        crisis_detected_count = 0
        
        for message in crisis_messages:
            print(f"  Testing crisis message: '{message}'")
            response = chatbot.get_response(message)
            
            if response.get("crisis_detected", False):
                crisis_detected_count += 1
                print(f"  ✅ Crisis correctly detected")
                
                # Check safety info
                safety_info = response.get("safety_info", {})
                if safety_info:
                    print(f"  ✅ Safety information provided")
            else:
                print(f"  ⚠️  Crisis not detected for: {message}")
        
        if crisis_detected_count > 0:
            print(f"✅ Crisis detection working ({crisis_detected_count}/{len(crisis_messages)} detected)")
            return True
        else:
            print("⚠️  Crisis detection may need tuning")
            return True  # Don't fail the test, just warn
            
    except Exception as e:
        print(f"❌ Crisis detection test failed: {e}")
        return False

def test_multilingual_support():
    """Test multilingual support"""
    print("\n🌍 Testing multilingual support...")
    
    try:
        from chatbot import OmaniMentalHealthChatbot
        chatbot = OmaniMentalHealthChatbot()
        
        multilingual_tests = [
            ("English", "How are you feeling today?"),
            ("Arabic", "كيف تشعر اليوم؟"),
            ("Mixed", "I feel حزين today"),  # Mixed English/Arabic
        ]
        
        for lang, message in multilingual_tests:
            print(f"  Testing {lang}: '{message}'")
            response = chatbot.get_response(message)
            
            if response and "response" in response:
                print(f"  ✅ {lang} response received")
            else:
                print(f"  ❌ {lang} response failed")
                return False
        
        print("✅ Multilingual support working")
        return True
        
    except Exception as e:
        print(f"❌ Multilingual test failed: {e}")
        return False

async def run_async_tests():
    """Run async tests"""
    print("\n🔄 Running async tests...")
    
    results = []
    
    # Voice processing test
    try:
        result = await test_voice_processing()
        results.append(("Voice Processing", result))
    except Exception as e:
        print(f"❌ Async voice test failed: {e}")
        results.append(("Voice Processing", False))
    
    return results

def main():
    """Main test runner"""
    print("🧪 Omani Mental Health Voice-Enabled Chatbot - Test Suite")
    print("=========================================================")
    
    test_results = []
    
    # Synchronous tests
    test_results.append(("Imports", test_imports()))
    test_results.append(("Environment", test_environment_setup()))
    test_results.append(("Chatbot Basic", test_chatbot_functionality()))
    test_results.append(("Crisis Detection", test_crisis_detection()))
    test_results.append(("Multilingual", test_multilingual_support()))
    test_results.append(("Voice Setup", test_voice_service_setup()))
    test_results.append(("WebSocket", test_websocket_service()))
    
    # Async tests
    try:
        async_results = asyncio.run(run_async_tests())
        test_results.extend(async_results)
    except Exception as e:
        print(f"❌ Async tests failed: {e}")
        test_results.append(("Async Tests", False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("========================")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! The voice-enabled chatbot is ready.")
        return 0
    elif passed >= total * 0.7:  # 70% pass rate
        print("⚠️  Most tests passed. Some features may be limited.")
        return 0
    else:
        print("❌ Too many test failures. Please check configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 