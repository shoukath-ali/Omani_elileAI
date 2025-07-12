# 🧠 Voice-Only Omani Arabic Mental Health Chatbot

**المساعد النفسي العماني الذكي | Intelligent Omani Mental Health Assistant**

A comprehensive mental health support chatbot that communicates exclusively through voice in Omani Arabic dialect, providing culturally sensitive, therapeutic-grade conversations with real-time speech processing capabilities.

## 🌟 Key Features

### 🎤 Voice-Only Interface
- **Whisper STT**: Advanced speech-to-text using OpenAI Whisper
- **Azure TTS**: Natural Omani Arabic voice synthesis
- **Real-time Processing**: <20 seconds end-to-end latency
- **Cultural Authenticity**: Authentic Omani Arabic dialect

### 🤖 Dual-Model AI System
- **Primary**: GPT-4o for conversational responses
- **Validation**: Claude Opus 4 for cultural sensitivity
- **Smart Fallback**: Seamless model switching
- **Crisis Detection**: Automatic emergency support

### 🕌 Cultural Integration
- **Islamic Values**: Religiously sensitive counseling
- **Gulf Culture**: Understanding of Omani social norms
- **Family Dynamics**: Culturally appropriate guidance
- **Traditional Wisdom**: Integration of Islamic counseling

### 🆘 Safety & Security
- **Crisis Intervention**: Automated risk assessment
- **Emergency Protocols**: Direct emergency service integration
- **Data Protection**: Privacy-first architecture
- **Professional Standards**: HIPAA-compliant handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Anthropic API Key
- Azure Speech Services Key
- Microphone access

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Omani_elileAI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export AZURE_SPEECH_KEY="your_azure_speech_key"
export AZURE_SPEECH_REGION="eastus"
```

4. **Run the application**
```bash
streamlit run app.py
```

## 🏗️ Architecture

```
Voice Input → Whisper STT → GPT-4o + Claude → Azure TTS → Voice Output
     ↓              ↓           ↓              ↓         ↓
  Audio Bytes → Arabic Text → AI Response → SSML → Audio Bytes
```

### Core Components

#### 📁 File Structure
```
Omani_elileAI/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration management
├── speech_service.py         # Whisper STT + Azure TTS
├── ai_service.py            # GPT-4o + Claude dual model
├── mental_health_bot.py     # Main bot coordination
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

#### 🔧 Services

1. **Speech Service** (`speech_service.py`)
   - Whisper-based speech recognition
   - Azure Neural TTS for Omani Arabic
   - Audio format conversion and optimization

2. **AI Service** (`ai_service.py`)
   - GPT-4o primary response generation
   - Claude Opus 4 cultural validation
   - Crisis detection algorithms

3. **Mental Health Bot** (`mental_health_bot.py`)
   - Main conversation coordination
   - Therapeutic context management
   - Session statistics and monitoring

## 🎯 Usage

### 🎤 Voice Interaction Flow

1. **🗣️ Speak**: Click microphone and speak in Omani Arabic
2. **📝 Recognize**: See your speech converted to text
3. **🤖 Process**: AI generates culturally appropriate response
4. **🔊 Listen**: Hear response in authentic Omani Arabic
5. **💬 Continue**: Natural conversation flow maintained

### 📊 Session Management

- **Real-time Stats**: Response times and performance metrics
- **Crisis Monitoring**: Automatic detection and intervention
- **Cultural Adaptation**: Context-aware therapeutic responses
- **Privacy Protection**: No conversation data retention

## 🌍 Cultural Sensitivity

### 🕌 Islamic Integration
- Quranic references when appropriate
- Dua and dhikr recommendations
- Halal therapeutic approaches
- Family and community values

### 🇴🇲 Omani Context
- Local cultural norms and expectations
- Traditional wisdom integration
- Community support emphasis
- Regional dialect authenticity

## 🆘 Crisis Support

### 🚨 Emergency Detection
- Automatic keyword monitoring
- Risk assessment algorithms
- Immediate intervention protocols
- Professional referral systems

### 📞 Emergency Contacts
- **Police**: 9999
- **Mental Health Hotline**: 24673000
- **Ministry of Health**: 24602077

## 🔧 Configuration

### Environment Variables
```bash
# AI Services
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Azure Speech
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=eastus

# Application Settings
MAX_RESPONSE_TIME=15
ENABLE_CRISIS_DETECTION=true
PRIMARY_LANGUAGE=ar-OM
CULTURAL_CONTEXT=gulf_arab
```

### Voice Configuration
- **Primary Voice**: ar-OM-AyshaNeural (Female)
- **Fallback Voice**: ar-OM-AbdullahNeural (Male)
- **Whisper Model**: base (configurable)
- **TTS Quality**: High neural synthesis

## 📈 Performance Targets

### ⚡ Latency Requirements
- **Total Response Time**: <20 seconds
- **STT Processing**: <3 seconds
- **AI Generation**: <10 seconds
- **TTS Synthesis**: <5 seconds

### 🎯 Quality Metrics
- **Speech Recognition**: >95% accuracy
- **Cultural Appropriateness**: Expert validated
- **Crisis Detection**: <1% false positives
- **User Satisfaction**: Therapeutic-grade quality

## 🚀 Deployment

### Azure App Service

1. **Create Azure resources**
```bash
az group create --name omani-mental-health-rg --location eastus
az appservice plan create --name omani-bot-plan --resource-group omani-mental-health-rg --sku B1
az webapp create --name omani-mental-health-bot --resource-group omani-mental-health-rg --plan omani-bot-plan
```

2. **Configure environment variables**
```bash
az webapp config appsettings set --name omani-mental-health-bot --resource-group omani-mental-health-rg --settings OPENAI_API_KEY="your_key" ANTHROPIC_API_KEY="your_key" AZURE_SPEECH_KEY="your_key"
```

3. **Deploy application**
```bash
az webapp deployment source config --name omani-mental-health-bot --resource-group omani-mental-health-rg --repo-url <your-repo> --branch main --manual-integration
```

## 🔒 Security & Privacy

### Data Protection
- **No Conversation Storage**: Sessions cleared after completion
- **Encrypted Communication**: TLS 1.3 for all API calls
- **Local Processing**: Minimal cloud data transmission
- **Audit Logging**: Crisis events only (with consent)

### Compliance
- **HIPAA-Ready**: Healthcare data protection standards
- **Cultural Ethics**: Islamic counseling guidelines
- **Professional Standards**: Licensed mental health practices
- **Regional Regulations**: Oman healthcare compliance

## 🧪 Testing

### Test Scenarios
1. **General Anxiety**: Everyday stress and worry counseling
2. **Family Issues**: Culturally sensitive relationship guidance
3. **Work Stress**: Career and professional development support
4. **Crisis Intervention**: Emergency mental health support
5. **Code-Switching**: Arabic-English mixed conversations

### Performance Validation
```bash
# Test system components
python -c "from mental_health_bot import test_bot_system; print(test_bot_system())"

# Test voice services
python -c "from speech_service import test_speech_services; print(test_speech_services())"
```

## 🤝 Contributing

### Development Guidelines
1. **Cultural Sensitivity**: All contributions must respect Islamic and Omani values
2. **Mental Health Standards**: Therapeutic-grade quality requirements
3. **Code Quality**: Comprehensive testing and documentation
4. **Privacy First**: No unnecessary data collection or storage

### Areas for Contribution
- 🌍 **Localization**: Additional Gulf Arabic dialects
- 🧠 **Therapy Techniques**: Advanced CBT adaptations
- 🔊 **Voice Quality**: Enhanced TTS naturalness
- 📱 **Platform Expansion**: Mobile app development

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI**: Whisper STT and GPT-4o model
- **Anthropic**: Claude Opus 4 validation system
- **Microsoft Azure**: Neural TTS services
- **Oman Ministry of Health**: Mental health guidelines
- **Islamic Counseling Community**: Cultural adaptation guidance

## 📞 Support

For technical support or mental health emergencies:

### 🆘 Emergency Support
- **Oman Emergency**: 9999
- **Mental Health Crisis**: 24673000

### 💬 Technical Support
- **Documentation**: [GitHub Issues](issues)
- **Community**: [Discussions](discussions)
- **Professional Consultation**: Available on request

---

**Built with ❤️ for the mental health and wellness of the Omani community**
**تم تطويره بحب لدعم الصحة النفسية والعافية للمجتمع العماني** 