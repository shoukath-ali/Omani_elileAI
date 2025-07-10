"""
Omani Mental Health Chatbot - Streamlit Frontend
A simple, compassionate mental health support chatbot
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Try importing chatbot with error handling
try:
    from chatbot import OmaniMentalHealthBot
except ImportError as e:
    st.error(f"Error importing chatbot: {e}")
    st.stop()

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Omani Mental Health Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with black background
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Sidebar background */
    .css-1d391kg {
        background-color: #111111;
    }
    
    /* Main content area */
    .block-container {
        background-color: #000000;
        padding-top: 2rem;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #00FF88, #00AAFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        color: #CCCCCC;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #333333;
    }
    
    .user-message {
        background-color: #1E3A8A;
        border-left: 4px solid #3B82F6;
        color: #FFFFFF;
    }
    
    .bot-message {
        background-color: #166534;
        border-left: 4px solid #22C55E;
        color: #FFFFFF;
    }
    
    .system-message {
        background-color: #1F2937;
        border-left: 4px solid #6B7280;
        color: #D1D5DB;
        font-style: italic;
    }
    
    .warning-message {
        background-color: #451A03;
        border-left: 4px solid #F59E0B;
        color: #FEF3C7;
    }
    
    .error-message {
        background-color: #7F1D1D;
        border-left: 4px solid #EF4444;
        color: #FEE2E2;
    }
    
    .transcription {
        background-color: #292524;
        border-left: 4px solid #F97316;
        color: #FDBA74;
        font-style: italic;
    }
    
    /* Warning and crisis boxes */
    .warning-box {
        background-color: #451A03;
        border: 2px solid #F59E0B;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #FEF3C7;
    }
    
    .crisis-box {
        background-color: #7F1D1D;
        border: 3px solid #EF4444;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #FEE2E2;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { border-color: #EF4444; }
        50% { border-color: #F87171; }
        100% { border-color: #EF4444; }
    }
    
    /* Buttons styling */
    .stButton > button {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 2px solid #374151;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #374151;
        border-color: #4B5563;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 255, 136, 0.3);
    }
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #00FF88, #00AAFF);
        color: #000000;
        border: none;
        font-weight: bold;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(45deg, #00AAFF, #00FF88);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 255, 136, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 2px solid #374151;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00FF88;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
    }
    
    .stTextArea > div > div > textarea {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 2px solid #374151;
        border-radius: 8px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #00FF88;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 2px solid #374151;
        border-radius: 8px;
    }
    
    /* Slider styling */
    .stSlider > div > div {
        background-color: #1F2937;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1F2937;
        color: #FFFFFF;
        border: 2px solid #374151;
        border-radius: 8px;
    }
    
    .streamlit-expanderContent {
        background-color: #111111;
        border: 2px solid #374151;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #111111;
        border-right: 2px solid #374151;
    }
    
    /* Sidebar text */
    .css-1d391kg .stMarkdown {
        color: #FFFFFF;
    }
    
    /* Metrics styling */
    .metric-container {
        background-color: #1F2937;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #374151;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #111111;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #374151;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4B5563;
    }
</style>
""", unsafe_allow_html=True)

def initialize_chatbot():
    """Initialize the chatbot with error handling"""
    try:
        return OmaniMentalHealthBot()
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {str(e)}")
        st.stop()

def display_crisis_resources():
    """Display crisis resources in sidebar"""
    st.sidebar.markdown("## 🆘 Crisis Resources")
    st.sidebar.markdown("""
    **If you're having thoughts of self-harm:**
    
    🇴🇲 **Oman:**
    - Emergency: 9999
    - Mental Health Helpline: Call your local health center
    
    🌍 **International:**
    - Crisis Text Line: Text HOME to 741741
    - International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
    
    **Remember: You're not alone, and help is available.**
    """)

def display_disclaimer():
    """Display important disclaimer"""
    with st.expander("⚠️ Important Disclaimer - Please Read"):
        st.markdown("""
        **This chatbot is for informational and emotional support purposes only.**
        
        - 🏥 **Not a replacement for professional medical care**
        - 👨‍⚕️ **Always consult healthcare professionals for medical advice**
        - 🆘 **In crisis situations, contact emergency services immediately**
        - 🔒 **Your conversations are not stored or shared**
        - 🇴🇲 **Designed with Omani cultural context in mind**
        
        By using this chatbot, you acknowledge these limitations and agree to seek professional help when needed.
        """)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🧠 Omani Mental Health Chatbot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your compassionate companion for mental wellness • رفيقك الرحيم للصحة النفسية</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🛠️ Settings")
    
    # Display crisis resources
    display_crisis_resources()
    
    # Model selection
    available_models = ["gpt-3.5-turbo", "gpt-4 (if available)", "claude-3-sonnet-20240229 (if available)"]
    selected_model_display = st.sidebar.selectbox(
        "Select AI Model",
        available_models,
        index=0,
        help="Choose the AI model for responses. GPT-3.5-turbo is most widely available."
    )
    
    # Map display names to actual model names
    model_mapping = {
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        "gpt-4 (if available)": "gpt-4",
        "claude-3-sonnet-20240229 (if available)": "claude-3-sonnet-20240229"
    }
    selected_model = model_mapping.get(selected_model_display, "gpt-3.5-turbo")
    
    # Model access info
    if selected_model != "gpt-3.5-turbo":
        st.sidebar.info("ℹ️ If the selected model is not accessible, the system will automatically fallback to GPT-3.5-turbo.")
    else:
        st.sidebar.success("✅ GPT-3.5-turbo is available to all OpenAI accounts.")
    
    # Temperature control
    temperature = st.sidebar.slider(
        "Response Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )
    
    # Language preference
    language = st.sidebar.selectbox(
        "Language / اللغة",
        ["English", "Arabic", "Both / كلاهما"],
        help="Select your preferred language"
    )
    
    # Display disclaimer
    display_disclaimer()
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = initialize_chatbot()
        st.session_state.chatbot.set_model(selected_model)
        st.session_state.chatbot.set_temperature(temperature)
        st.session_state.chatbot.set_language(language)
    
    # Update chatbot settings if changed
    if (st.session_state.get('prev_model') != selected_model or 
        st.session_state.get('prev_temp') != temperature or
        st.session_state.get('prev_lang') != language):
        
        st.session_state.chatbot.set_model(selected_model)
        st.session_state.chatbot.set_temperature(temperature)
        st.session_state.chatbot.set_language(language)
        st.session_state.prev_model = selected_model
        st.session_state.prev_temp = temperature
        st.session_state.prev_lang = language
        
        # Add a system message about model change
        if st.session_state.get('prev_model') != selected_model and st.session_state.get('prev_model') is not None:
            st.session_state.chat_history.append({
                'role': 'system',
                'content': f'🔄 Model changed to {selected_model_display}. Conversation continues...',
                'timestamp': datetime.now()
            })
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # Add welcome message
        welcome_msg = st.session_state.chatbot.get_welcome_message()
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': welcome_msg,
            'timestamp': datetime.now()
        })
        # Add system status message
        st.session_state.chat_history.append({
            'role': 'system',
            'content': '🌙 Dark mode activated. All systems ready. Your privacy is protected.',
            'timestamp': datetime.now()
        })
    
    # Chat interface
    st.markdown("## 💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            elif message['role'] == 'assistant':
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>Assistant ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            elif message['role'] == 'system':
                st.markdown(f"""
                <div class="chat-message system-message">
                    <strong>System ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            elif message['role'] == 'warning':
                st.markdown(f"""
                <div class="chat-message warning-message">
                    <strong>Warning ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            elif message['role'] == 'error':
                st.markdown(f"""
                <div class="chat-message error-message">
                    <strong>Error ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            elif message['role'] == 'transcription':
                st.markdown(f"""
                <div class="chat-message transcription">
                    <strong>Transcribed ({message['timestamp'].strftime('%H:%M')}):</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("### 🎯 Quick Start")
    st.markdown("**Choose a topic to begin your conversation:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😰 I'm feeling anxious", key="anxiety_btn", help="Get support for anxiety and worry"):
            user_input = "I'm feeling anxious and worried. Can you help me?"
            process_user_input(user_input)
            st.rerun()
    
    with col2:
        if st.button("😴 Having trouble sleeping", key="sleep_btn", help="Get tips for better sleep"):
            user_input = "I'm having trouble sleeping and my mind is racing at night."
            process_user_input(user_input)
            st.rerun()
    
    with col3:
        if st.button("💼 Work stress", key="work_btn", help="Manage work-related stress"):
            user_input = "I'm feeling overwhelmed with work stress. What can I do?"
            process_user_input(user_input)
            st.rerun()
    
    # Additional quick buttons row
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("💭 Need someone to talk", key="talk_btn", help="General emotional support"):
            user_input = "I just need someone to talk to about how I'm feeling."
            process_user_input(user_input)
            st.rerun()
    
    with col5:
        if st.button("🕌 Faith and healing", key="faith_btn", help="Islamic perspective on healing"):
            user_input = "Can you help me understand healing and patience from an Islamic perspective?"
            process_user_input(user_input)
            st.rerun()
    
    with col6:
        if st.button("🤲 Need guidance", key="guidance_btn", help="Spiritual guidance and support"):
            user_input = "I'm looking for guidance and spiritual support in difficult times."
            process_user_input(user_input)
            st.rerun()
    
    # Text input
    st.markdown("### ✏️ Type your message")
    user_input = st.text_area(
        "Share what's on your mind...",
        placeholder="Type your thoughts, feelings, or questions here...",
        height=100,
        key="user_input"
    )
    
    # Send button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        send_button = st.button("Send 📤", type="primary")
    with col2:
        clear_button = st.button("Clear Chat 🗑️")
    
    # Process input
    if send_button and user_input.strip():
        process_user_input(user_input.strip())
        st.rerun()
    
    # Clear chat
    if clear_button:
        st.session_state.chat_history = []
        # Add welcome message back
        welcome_msg = st.session_state.chatbot.get_welcome_message()
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': welcome_msg,
            'timestamp': datetime.now()
        })
        # Add system status message
        st.session_state.chat_history.append({
            'role': 'system',
            'content': '🌙 Chat cleared. Dark mode active. Ready for new conversation.',
            'timestamp': datetime.now()
        })
        st.rerun()
    
    # Statistics in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Session Stats")
    total_messages = len(st.session_state.chat_history)
    user_messages = len([m for m in st.session_state.chat_history if m['role'] == 'user'])
    st.sidebar.metric("Total Messages", total_messages)
    st.sidebar.metric("Your Messages", user_messages)
    
    # Feedback
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Feedback")
    feedback = st.sidebar.text_area("How can we improve?", height=100)
    if st.sidebar.button("Submit Feedback"):
        st.sidebar.success("Thank you for your feedback!")

def process_user_input(user_input):
    """Process user input and get chatbot response"""
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    })
    
    # Show thinking spinner
    with st.spinner("🤖 Thinking..."):
        try:
            # Check for crisis indicators first
            crisis_detected = st.session_state.chatbot.detect_crisis(user_input)
            
            if crisis_detected:
                # Add crisis warning to chat
                st.session_state.chat_history.append({
                    'role': 'warning',
                    'content': '🚨 Crisis support detected. Please see emergency resources.',
                    'timestamp': datetime.now()
                })
                
                # Display crisis warning box
                st.markdown("""
                <div class="crisis-box">
                    <h4>🚨 Crisis Support Detected</h4>
                    <p>I notice you might be going through a difficult time. Please consider reaching out to a crisis helpline or emergency services if you need immediate help.</p>
                    <p><strong>🇴🇲 Oman Emergency: 9999</strong></p>
                    <p><strong>🌍 International Crisis Line: Text HOME to 741741</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Get response from chatbot
            response = st.session_state.chatbot.get_response(
                user_input, 
                st.session_state.chat_history
            )
            
            # Add bot response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            error_response = f"I apologize, but I'm having trouble responding right now. Error: {str(e)}"
            st.session_state.chat_history.append({
                'role': 'error',
                'content': error_response,
                'timestamp': datetime.now()
            })
    
    # Clear the input
    st.session_state.user_input = ""

if __name__ == "__main__":
    main() 