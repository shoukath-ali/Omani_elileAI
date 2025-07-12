"""
Voice-Only Omani Arabic Mental Health Chatbot
Main Streamlit Application
"""

import streamlit as st
import asyncio
import base64
import logging
from datetime import datetime
from typing import Dict, Any

# Import bot components
from mental_health_bot import process_user_voice, get_bot_stats, test_bot_system, reset_bot_session
from config import settings

# Audio recording component
try:
    from streamlit_mic_recorder import mic_recorder
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    st.error("Audio recording not available. Please install: pip install streamlit-mic-recorder")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="المساعد النفسي العماني | Omani Mental Health Assistant",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .voice-recorder {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        margin: 2rem 0;
        color: white;
    }
    
    .stats-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .crisis-alert {
        background: #ffe6e6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #e6ffe6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        color: black;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 المساعد النفسي العماني</h1>
        <h2>Omani Mental Health Assistant</h2>
        <p>مساعد الصحة النفسية الذكي باللهجة العمانية الأصيلة</p>
        <p>Voice-Only AI Mental Health Support in Authentic Omani Arabic</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with settings and stats"""
    with st.sidebar:
        st.markdown("### ⚙️ إعدادات | Settings")
        
        # System status
        if st.button("🔍 Test System | اختبار النظام"):
            with st.spinner("Testing system components..."):
                test_results = test_bot_system()
                
                if test_results["overall_status"] == "healthy":
                    st.success("✅ All systems operational")
                elif test_results["overall_status"] == "partial":
                    st.warning("⚠️ Some services unavailable")
                else:
                    st.error("❌ System issues detected")
                
                # Show detailed results
                with st.expander("Detailed Results"):
                    st.json(test_results)
        
        st.markdown("---")
        
        # Session management
        st.markdown("### 📊 Session | الجلسة")
        
        if st.button("🔄 New Session | جلسة جديدة"):
            reset_bot_session()
            st.session_state.conversation_history = []
            st.session_state.current_session_id = None
            st.success("Session reset successfully")
            st.rerun()
        
        # Show current stats
        stats = get_bot_stats()
        
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        st.metric("Conversations", stats.get("conversation_count", 0))
        
        avg_time = stats.get("avg_response_time", 0)
        target_met = "✅" if stats.get("performance_target_met", False) else "⚠️"
        st.metric(
            f"Avg Response Time {target_met}", 
            f"{avg_time}s",
            delta=f"Target: <{settings.max_response_time}s"
        )
        
        crises = stats.get("total_crises_detected", 0)
        if crises > 0:
            st.metric("🚨 Crises Detected", crises)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Emergency contacts
        st.markdown("### 🆘 Emergency | طوارئ")
        st.markdown("""
        **Oman Emergency Numbers:**
        - 🚨 Police: **9999**
        - 🏥 Mental Health: **24673000**
        - 🩺 Ministry of Health: **24602077**
        """)

def render_voice_interface():
    """Render the main voice recording interface"""
    if not AUDIO_AVAILABLE:
        st.error("❌ Audio recording not available. Please install streamlit-mic-recorder.")
        return
    
    st.markdown("""
    <div class="voice-recorder">
        <h3>🎤 اضغط للتحدث | Click to Speak</h3>
        <p>تحدث بالعربية العمانية وسأستمع إليك | Speak in Omani Arabic and I'll listen</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice recorder
    audio = mic_recorder(
        start_prompt="🎤 ابدأ التحدث | Start Speaking",
        stop_prompt="⏹️ أوقف التسجيل | Stop Recording",
        just_once=False,
        use_container_width=True,
        callback=None,
        args=(),
        kwargs={},
        key='voice_recorder'
    )
    
    # Process audio if received
    if audio is not None and not st.session_state.processing:
        if isinstance(audio, dict) and 'bytes' in audio:
            audio_bytes = audio['bytes']
        else:
            audio_bytes = audio
        
        if audio_bytes and len(audio_bytes) > 1000:  # Minimum audio size
            st.session_state.processing = True
            process_voice_message(audio_bytes)

def process_voice_message(audio_bytes: bytes):
    """Process voice message through the mental health bot"""
    
    try:
        with st.spinner("🎤 معالجة الصوت... | Processing voice..."):
            # Use asyncio to run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(process_user_voice(audio_bytes))
            finally:
                loop.close()
        
        if result["success"]:
            # Add to conversation history
            conversation_entry = {
                "timestamp": datetime.now(),
                "user_text": result["user_text"],
                "response_text": result["response_text"],
                "audio_data": result["audio_data"],
                "crisis_detected": result.get("crisis_detected", False),
                "processing_time": result["processing_time"]
            }
            
            st.session_state.conversation_history.append(conversation_entry)
            
            # Show success
            st.markdown(f"""
            <div class="success-message">
                ✅ <strong>Response processed in {result['processing_time']:.2f}s</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Show crisis alert if detected
            if result.get("crisis_detected", False):
                st.markdown("""
                <div class="crisis-alert">
                    🚨 <strong>Crisis Support Activated</strong><br>
                    Emergency resources have been included in the response.
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"❌ System error: {str(e)}")
        logger.error(f"Voice processing error: {e}")
    
    finally:
        st.session_state.processing = False

def render_conversation_history():
    """Render conversation history"""
    if not st.session_state.conversation_history:
        st.info("""
        ### 🌟 Welcome | أهلاً وسهلاً
        
        **Voice-Only Mental Health Support in Omani Arabic**
        **دعم الصحة النفسية بالصوت فقط باللهجة العمانية**
        
        Click the microphone above and start speaking in Omani Arabic.
        اضغط على الميكروفون أعلاه وابدأ بالتحدث بالعربية العمانية.
        
        I'm here to listen and provide culturally sensitive mental health support.
        أنا هنا لأستمع إليك وأقدم لك الدعم النفسي المناسب ثقافياً.
        """)
        return
    
    st.markdown("### 💬 المحادثة | Conversation")
    
    for i, entry in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # User message
                st.markdown(f"**🧑‍💼 You | أنت:**")
                st.markdown(f"> {entry['user_text']}")
                
                # AI response
                st.markdown(f"**🤖 Assistant | المساعد:**")
                st.markdown(f"> {entry['response_text']}")
                
                # Audio player
                if entry.get("audio_data"):
                    st.markdown("**🔊 Audio Response | الرد الصوتي:**")
                    audio_bytes = entry["audio_data"]
                    st.audio(audio_bytes, format="audio/wav")
            
            with col2:
                st.markdown(f"**Time:** {entry['processing_time']:.2f}s")
                
                if entry.get("crisis_detected", False):
                    st.markdown("🚨 **Crisis Detected**")
                
                timestamp = entry["timestamp"].strftime("%H:%M:%S")
                st.markdown(f"**🕐** {timestamp}")
            
            st.markdown("---")

def main():
    """Main application"""
    try:
        initialize_session_state()
        
        # Render components
        render_header()
        render_sidebar()
        render_voice_interface()
        render_conversation_history()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #666;">
            <p>🔒 Your privacy is protected | خصوصيتك محمية</p>
            <p>For emergencies, call 9999 | في حالة الطوارئ، اتصل بـ 9999</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Main app error: {e}")
        
        if st.button("🔄 Restart Application"):
            st.rerun()

if __name__ == "__main__":
    main() 