"""
Omani Mental Health Voice-Enabled Chatbot
Enhanced with Azure Speech Services for real-time voice interaction
"""

import streamlit as st
import asyncio
import base64
import time
import logging
from typing import Dict, Any, Optional
import io
import tempfile

# Configure page FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="المساعد النفسي العماني الصوتي | Omani Voice Mental Health Assistant",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our services after page config
from chatbot import OmaniMentalHealthChatbot
from voice_service import get_voice_service, test_voice_setup, sync_speech_to_text, sync_text_to_speech

# Streamlit audio recording imports
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    from streamlit_mic_recorder import mic_recorder
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dark theme CSS with voice interface styling
DARK_THEME_CSS = """
<style>
/* Main app background */
.stApp {
    background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
    color: #FFFFFF;
}

/* Sidebar */
.css-1d391kg {
    background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
    border-right: 2px solid #00FF88;
}

/* Voice interface controls */
.voice-controls {
    background: linear-gradient(135deg, #111111, #222222);
    border: 2px solid #00FF88;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
}

.voice-status {
    background: linear-gradient(90deg, #00FF88, #00AAFF);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: bold;
    font-size: 1.2em;
    text-align: center;
    padding: 10px;
    animation: pulse 2s infinite;
}

/* Voice buttons */
.voice-button {
    background: linear-gradient(45deg, #00FF88, #00AAFF);
    border: none;
    border-radius: 50%;
    width: 80px;
    height: 80px;
    margin: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2em;
}

.voice-button:hover {
    transform: scale(1.1);
    box-shadow: 0 0 30px rgba(0, 255, 136, 0.8);
}

.recording {
    animation: pulse 1s infinite;
    box-shadow: 0 0 50px rgba(255, 0, 0, 0.8);
    background: linear-gradient(45deg, #FF0000, #FF6600);
}

/* Chat messages with voice indicators */
.user-message {
    background: linear-gradient(135deg, #001122, #003344);
    border-left: 4px solid #00FF88;
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    position: relative;
}

.bot-message {
    background: linear-gradient(135deg, #220011, #330022);
    border-left: 4px solid #00AAFF;
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    position: relative;
}

.voice-indicator {
    position: absolute;
    top: 5px;
    right: 10px;
    font-size: 1.2em;
    opacity: 0.7;
}

/* Audio player styling */
.stAudio {
    border-radius: 10px;
    background: #111111;
    border: 1px solid #00FF88;
}

/* Processing status */
.processing-status {
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: #000000;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    margin: 10px 0;
    animation: pulse 1.5s infinite;
}

/* Latency indicator */
.latency-good { color: #00FF88; }
.latency-ok { color: #FFD700; }
.latency-poor { color: #FF6600; }
.latency-bad { color: #FF0000; }

/* Voice quality indicator */
.voice-quality {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    background: rgba(0, 255, 136, 0.1);
    border-radius: 10px;
    margin: 10px 0;
}

.quality-bar {
    width: 100%;
    height: 8px;
    background: #333333;
    border-radius: 4px;
    overflow: hidden;
}

.quality-fill {
    height: 100%;
    transition: width 0.3s ease;
}

/* Crisis alert for voice mode */
.voice-crisis-alert {
    background: linear-gradient(45deg, #FF0000, #FF6600);
    color: #FFFFFF;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
    border: 3px solid #FFFFFF;
    animation: emergency-pulse 1s infinite;
    box-shadow: 0 0 50px rgba(255, 0, 0, 0.8);
}

@keyframes emergency-pulse {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
    100% { transform: scale(1); opacity: 1; }
}

/* Animations */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = f"session_{int(time.time())}"
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = OmaniMentalHealthChatbot()
    if 'voice_service' not in st.session_state:
        st.session_state.voice_service = get_voice_service()
    if 'voice_enabled' not in st.session_state:
        st.session_state.voice_enabled = True
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'last_audio' not in st.session_state:
        st.session_state.last_audio = None
    if 'voice_stats' not in st.session_state:
        st.session_state.voice_stats = {
            'total_interactions': 0,
            'avg_latency': 0,
            'successful_stt': 0,
            'successful_tts': 0
        }

def render_voice_controls():
    """Render voice interface controls"""
    st.markdown('<div class="voice-controls">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎤 واجهة صوتية | Voice Interface")
        
        # Voice service status
        voice_status = test_voice_setup()
        if voice_status["success"]:
            status_color = "latency-good"
            status_text = "✅ Voice service active"
        else:
            status_color = "latency-bad"
            status_text = f"❌ Voice service error: {voice_status.get('error', 'Unknown')}"
        
        st.markdown(f'<div class="{status_color}">{status_text}</div>', unsafe_allow_html=True)
        
        # Audio recording section
        if AUDIO_AVAILABLE:
            st.markdown("#### Record your voice:")
            
            # Use streamlit-mic-recorder
            audio_data = mic_recorder(
                start_prompt="🎤 Start Recording",
                stop_prompt="⏹️ Stop Recording",
                key="voice_recorder",
                format="wav",
                just_once=False
            )
            
            if audio_data is not None:
                st.session_state.last_audio = audio_data
                st.success("Audio recorded! Processing...")
                process_voice_input(audio_data['bytes'])
        else:
            st.warning("Audio recording not available. Install: pip install streamlit-webrtc streamlit-mic-recorder")
            
        # Voice settings
        with st.expander("🔧 Voice Settings"):
            col_a, col_b = st.columns(2)
            
            with col_a:
                voice_quality = st.selectbox(
                    "Voice Quality",
                    ["high", "medium", "low"],
                    index=0
                )
                
            with col_b:
                voice_speed = st.slider(
                    "Speech Speed",
                    min_value=0.5,
                    max_value=2.0,
                    value=0.9,
                    step=0.1
                )
                
        # Voice statistics
        stats = st.session_state.voice_stats
        st.markdown("#### 📊 Voice Statistics")
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.metric("Total Interactions", stats['total_interactions'])
        with col_s2:
            latency_class = get_latency_class(stats['avg_latency'])
            st.metric("Avg Latency", f"{stats['avg_latency']:.2f}s")
        with col_s3:
            success_rate = (stats['successful_stt'] / max(stats['total_interactions'], 1)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_latency_class(latency: float) -> str:
    """Get CSS class for latency indicator"""
    if latency < 5:
        return "latency-good"
    elif latency < 10:
        return "latency-ok"
    elif latency < 20:
        return "latency-poor"
    else:
        return "latency-bad"


def process_voice_input(audio_bytes: bytes):
    """Process voice input synchronously"""
    try:
        # Since we now use sync functions, we can call directly
        process_voice_input_sync(audio_bytes)
    except Exception as e:
        logger.error(f"Error in voice processing: {e}")
        st.error(f"Voice processing error: {str(e)}")

def process_voice_input_sync(audio_bytes: bytes):
    """Process voice input synchronously"""
    try:
        # Convert speech to text
        stt_result = sync_speech_to_text(audio_bytes)
        
        if not stt_result["success"]:
            st.error(f"Speech recognition failed: {stt_result.get('error', 'Unknown error')}")
            return
        
        user_text = stt_result["text"]
        if not user_text.strip():
            st.warning("No speech detected. Please try again.")
            return
        
        # Update statistics
        st.session_state.voice_stats['total_interactions'] += 1
        st.session_state.voice_stats['successful_stt'] += 1
        
        # Display transcription
        st.markdown(f'<div class="user-message">🎤 **You said:** {user_text}</div>', unsafe_allow_html=True)
        
        # Process with chatbot (with conversation history for memory)
        with st.spinner("جاري التفكير... | Thinking..."):
            response = st.session_state.chatbot.get_response(
                user_text, 
                chat_history=st.session_state.messages,  # Pass conversation history
                conversation_id=st.session_state.conversation_id
            )
        
        # Generate speech response
        with st.spinner("جاري تحويل الرد إلى صوت... | Converting to speech..."):
            tts_result = sync_text_to_speech(response["response"])
        
        if tts_result["success"]:
            # Display bot response with audio
            st.markdown(f'<div class="bot-message">🤖 **Assistant:** {response["response"]}</div>', unsafe_allow_html=True)
            
            # Play audio response
            st.audio(tts_result["audio_data"], format="audio/wav")
            
            st.session_state.voice_stats['successful_tts'] += 1
        else:
            # Fallback to text-only response
            st.markdown(f'<div class="bot-message">🤖 **Assistant:** {response["response"]}</div>', unsafe_allow_html=True)
            st.warning(f"Voice synthesis failed: {tts_result.get('error', 'Unknown error')}")
        
        # Handle crisis detection
        if response.get("crisis_detected", False):
            display_voice_crisis_alert(response.get("safety_info", {}))
        
        # Update conversation history
        st.session_state.messages.append({"role": "user", "content": user_text, "type": "voice"})
        st.session_state.messages.append({"role": "assistant", "content": response["response"], "type": "voice"})
        
        # Update latency statistics (fix calculation to use actual processing times)
        stt_time = stt_result.get("processing_time", 0)  # Actual STT processing time
        response_time = response.get("response_time", 0)  # AI response time
        tts_time = tts_result.get("processing_time", 0)  # Actual TTS processing time
        
        total_latency = stt_time + response_time + tts_time
        current_avg = st.session_state.voice_stats['avg_latency']
        total_interactions = st.session_state.voice_stats['total_interactions']
        
        # Only update if we have valid timing data
        if total_latency > 0:
            st.session_state.voice_stats['avg_latency'] = ((current_avg * (total_interactions - 1)) + total_latency) / total_interactions
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        st.error(f"Voice processing failed: {str(e)}")

def display_voice_crisis_alert(safety_info: Dict[str, Any]):
    """Display crisis alert for voice interactions"""
    st.markdown("""
    <div class="voice-crisis-alert">
        <h2>🚨 EMERGENCY DETECTED | تم اكتشاف حالة طوارئ</h2>
        <h3>Immediate Help Available | المساعدة الفورية متاحة</h3>
        <p><strong>Oman Emergency: 9999</strong></p>
        <p><strong>You are not alone. Professional help is available.</strong></p>
        <p><strong>أنت لست وحدك. المساعدة المهنية متاحة.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-play emergency audio message
    try:
        emergency_text = "هذه حالة طوارئ. اتصل بالرقم 9999 للحصول على المساعدة الفورية."
        tts_result = sync_text_to_speech(emergency_text)
        
        if tts_result["success"]:
            st.audio(tts_result["audio_data"], format="audio/wav", autoplay=True)
    except:
        pass  # Fail silently for emergency audio

def render_conversation_history():
    """Render conversation history with voice indicators"""
    st.markdown("### 💬 Conversation History | سجل المحادثة")
    
    for message in st.session_state.messages[-10:]:  # Show last 10 messages
        is_voice = message.get("type") == "voice"
        voice_icon = "🎤" if is_voice else "⌨️"
        
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <span class="voice-indicator">{voice_icon}</span>
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <span class="voice-indicator">{voice_icon}</span>
                <strong>Assistant:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)

def render_text_fallback():
    """Render text input as fallback option"""
    st.markdown("### ⌨️ Text Input (Fallback) | الإدخال النصي")
    
    user_input = st.text_input(
        "Type your message | اكتب رسالتك:",
        key="text_input",
        placeholder="How are you feeling today? | كيف تشعر اليوم؟"
    )
    
    if st.button("Send Message | إرسال الرسالة") and user_input:
        # Process text input (with conversation history for memory)
        with st.spinner("Processing... | جاري المعالجة..."):
            response = st.session_state.chatbot.get_response(
                user_input, 
                chat_history=st.session_state.messages,  # Pass conversation history
                conversation_id=st.session_state.conversation_id
            )
        
        # Display response
        st.markdown(f'<div class="user-message">⌨️ **You:** {user_input}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="bot-message">🤖 **Assistant:** {response["response"]}</div>', unsafe_allow_html=True)
        
        # Handle crisis detection
        if response.get("crisis_detected", False):
            display_voice_crisis_alert(response.get("safety_info", {}))
        
        # Update conversation history
        st.session_state.messages.append({"role": "user", "content": user_input, "type": "text"})
        st.session_state.messages.append({"role": "assistant", "content": response["response"], "type": "text"})
        
        # Clear input
        st.session_state.text_input = ""

def render_quick_actions():
    """Render quick action buttons with voice support"""
    st.markdown("### ⚡ Quick Actions | إجراءات سريعة")
    
    col1, col2, col3 = st.columns(3)
    
    quick_actions = [
        ("😟 Feeling anxious", "أشعر بالقلق"),
        ("😢 Feeling sad", "أشعر بالحزن"),
        ("😰 Having panic", "أعاني من نوبة هلع"),
        ("🤲 Need Islamic guidance", "أحتاج إرشاد إسلامي"),
        ("💭 Negative thoughts", "أفكار سلبية"),
        ("🆘 Crisis help", "أحتاج مساعدة فورية")
    ]
    
    for i, (english, arabic) in enumerate(quick_actions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(f"{english}\n{arabic}", key=f"quick_{i}"):
                # Process quick action as voice input if enabled
                combined_text = f"{english} - {arabic}"
                
                if st.session_state.voice_enabled:
                    # Generate TTS for the quick action
                    try:
                        tts_result = sync_text_to_speech(arabic)
                        
                        if tts_result["success"]:
                            st.audio(tts_result["audio_data"], format="audio/wav")
                    except:
                        pass
                
                # Process with chatbot (with conversation history for memory)
                response = st.session_state.chatbot.get_response(
                    combined_text, 
                    chat_history=st.session_state.messages,  # Pass conversation history
                    conversation_id=st.session_state.conversation_id
                )
                
                # Display and process response
                st.markdown(f'<div class="user-message">⚡ **Quick Action:** {combined_text}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bot-message">🤖 **Assistant:** {response["response"]}</div>', unsafe_allow_html=True)
                
                # Generate voice response if enabled
                if st.session_state.voice_enabled:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        tts_result = loop.run_until_complete(generate_speech_output(response["response"]))
                        loop.close()
                        
                        if tts_result["success"]:
                            st.audio(tts_result["audio_data"], format="audio/wav")
                    except:
                        pass

def main():
    """Main application function"""
    # Apply dark theme
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # App header
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #00FF88;">🎤 المساعد النفسي العماني الصوتي</h1>
        <h2 style="color: #00AAFF;">Omani Voice Mental Health Assistant</h2>
        <p style="color: #CCCCCC;">AI-powered voice assistant for mental health support in Omani Arabic</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 Settings | الإعدادات")
        
        # Voice toggle
        st.session_state.voice_enabled = st.checkbox(
            "Enable Voice Interface | تفعيل الواجهة الصوتية",
            value=st.session_state.voice_enabled
        )
        
        # Language selection
        language = st.selectbox(
            "Interface Language | لغة الواجهة",
            ["العربية العمانية (Omani Arabic)", "English", "Both | كلاهما"],
            index=2
        )
        
        # Model selection
        model = st.selectbox(
            "AI Model | نموذج الذكاء الاصطناعي",
            ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"],
            index=0
        )
        
        # Voice service test
        if st.button("Test Voice Service | اختبار الخدمة الصوتية"):
            status = test_voice_setup()
            if status["success"]:
                st.success("✅ Voice service working")
            else:
                st.error(f"❌ Error: {status['error']}")
        
        # Clear conversation
        if st.button("Clear Conversation | مسح المحادثة"):
            st.session_state.messages = []
            st.session_state.conversation_id = f"session_{int(time.time())}"
            st.success("Conversation cleared | تم مسح المحادثة")
    
    # Main content area
    if st.session_state.voice_enabled:
        render_voice_controls()
        st.markdown("---")
    
    # Quick actions
    render_quick_actions()
    st.markdown("---")
    
    # Text fallback
    render_text_fallback()
    st.markdown("---")
    
    # Conversation history
    render_conversation_history()
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #666666;">
        <p>🔒 Privacy-first design | تصميم يحمي الخصوصية</p>
        <p>For emergencies, call 9999 | للطوارئ، اتصل على 9999</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 