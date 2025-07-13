flowchart TD
    A[🎤 User Speaks<br/>Omani Arabic] --> B[📹 Audio Recording<br/>streamlit-mic-recorder]
    B --> C[🔍 Audio Validation<br/>Min 1000 bytes]
    
    C --> D{📏 Audio Size<br/>Check}
    D -->|Too Small| E[❌ Error: No Speech<br/>Duration & Volume Info]
    D -->|Valid| F[⬆️ Upload to Whisper<br/>OpenAI API]
    
    F --> G[🔊 Speech-to-Text<br/>Arabic Recognition]
    G --> H{📝 Text Valid?}
    H -->|Empty| I[❌ Error: No Speech<br/>+ Audio Analysis]
    H -->|Valid| J[✅ Arabic Text<br/>Extracted]
    
    J --> K[🤖 AI Processing<br/>GPT-4o + Claude]
    K --> L[🔍 Crisis Detection<br/>Arabic & Mixed Keywords]
    
    L --> M{🚨 Crisis<br/>Detected?}
    M -->|Yes| N[🚨 Emergency Response<br/>+ Crisis Resources]
    M -->|No| O[💬 Normal Response<br/>Cultural Context]
    
    N --> P[🔊 Azure TTS<br/>Omani Voice Synthesis]
    O --> P
    
    P --> Q[🎵 Audio Response<br/>ar-OM-AyshaNeural]
    Q --> R[📱 Streamlit Playback<br/>User Interface]
    R --> S[👤 User Hears<br/>Response]
    
    T[📊 Performance Metrics<br/>Response Time: &lt;20s] --> U[📈 Session Stats<br/>Conversation Count]
    K --> T
    
    V[🔒 Privacy Protection<br/>No Data Storage] --> W[🗑️ Auto-Cleanup<br/>Session End]
    S --> V
    
    style A fill:#e3f2fd
    style G fill:#f3e5f5
    style K fill:#e8f5e8
    style M fill:#fff3e0
    style N fill:#ffebee
    style P fill:#fce4ec
    style T fill:#f1f8e9
    style V fill:#e0f2f1