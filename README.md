# 🧠 Omani Mental Health Chatbot

A compassionate AI-powered mental health support chatbot designed specifically for Omani culture, built with Streamlit and LangChain.

## ✨ Features

- **Cultural Sensitivity**: Designed with Omani culture and Islamic values in mind
- **Multilingual Support**: English, Arabic, and bilingual conversations
- **Crisis Detection**: Automatic detection and appropriate response to crisis situations
- **Multiple AI Models**: Support for GPT-3.5, GPT-4, and Claude models
- **Simple Interface**: Clean, user-friendly Streamlit interface
- **Azure Deployment**: Ready for deployment to Azure Web App

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenAI API key (required)
- Anthropic API key (optional, for Claude models)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Omani_elileAI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp environment.example .env
   ```
   
   Edit `.env` file and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501`

## 🌐 Azure Deployment

### Step 1: Create Azure Web App

1. **Create Azure Web App**
   ```bash
   # Using Azure CLI
   az webapp create \
     --resource-group your-resource-group \
     --plan your-app-service-plan \
     --name your-app-name \
     --runtime "PYTHON|3.11"
   ```

2. **Configure Application Settings**
   In Azure Portal, go to your Web App → Configuration → Application Settings:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   WEBSITES_PORT=8000
   ```

### Step 2: Set up GitHub Actions

1. **Get Publish Profile**
   - In Azure Portal, go to your Web App → Overview
   - Click "Get publish profile" and download the file
   - Copy the content

2. **Configure GitHub Secrets**
   In your GitHub repository, go to Settings → Secrets and variables → Actions:
   ```
   AZURE_WEBAPP_NAME=your-app-name
   AZURE_WEBAPP_PUBLISH_PROFILE=<paste publish profile content>
   ```

3. **Deploy**
   - Push your code to the `main` branch
   - GitHub Actions will automatically deploy to Azure
   - Your app will be available at `https://your-app-name.azurewebsites.net`

## 🛠️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT models |
| `ANTHROPIC_API_KEY` | No | Anthropic API key for Claude models |
| `APP_NAME` | No | Application name (default: "Omani Mental Health Chatbot") |
| `DEBUG` | No | Debug mode (default: true) |
| `DEFAULT_MODEL` | No | Default AI model (default: "gpt-3.5-turbo") |
| `MAX_TOKENS` | No | Maximum response length (default: 1000) |
| `TEMPERATURE` | No | AI creativity level (default: 0.7) |

### Supported Models

- **OpenAI Models**: gpt-3.5-turbo, gpt-4, gpt-4-turbo
- **Anthropic Models**: claude-3-sonnet-20240229, claude-3-haiku-20240307

## 🔒 Safety Features

### Crisis Detection
- Automatic detection of suicide/self-harm keywords
- Immediate display of crisis resources
- Culturally appropriate emergency contacts for Oman

### Privacy
- No conversation storage
- No personal data collection
- Secure API communication

### Cultural Sensitivity
- Islamic values integration
- Omani cultural context
- Appropriate mental health guidance

## 📱 Usage

### Quick Start Buttons
- **😰 I'm feeling anxious**: For anxiety and worry support
- **😴 Having trouble sleeping**: For sleep-related issues
- **💼 Work stress**: For work-life balance guidance

### Language Options
- **English**: Full English conversation
- **Arabic**: Full Arabic conversation (العربية)
- **Both**: Bilingual responses

### Crisis Resources

**🇴🇲 Oman Emergency Contacts:**
- Emergency: 9999
- Sultan Qaboos University Hospital: 24141414
- Royal Hospital: 24599000

**🌍 International:**
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: iasp.info

## 🧪 Testing

```bash
# Test the chatbot locally
streamlit run app.py

# Test different configurations
python test_chatbot.py
```

## 📄 Project Structure

```
Omani_elileAI/
├── app.py                    # Streamlit frontend
├── chatbot.py               # LangChain backend
├── requirements.txt         # Python dependencies
├── environment.example      # Environment variables template
├── startup.sh              # Azure startup script
├── .github/workflows/      # GitHub Actions
│   └── azure-deploy.yml   # Azure deployment workflow
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ⚠️ Important Disclaimers

- **Not a Medical Device**: This chatbot is for emotional support only
- **Professional Help**: Always consult healthcare professionals for medical advice
- **Crisis Situations**: Contact emergency services immediately in crisis situations
- **Cultural Context**: Designed specifically for Omani/GCC culture

## 📞 Support

For technical support or questions:
- Create an issue in this repository
- Contact: [your-email@domain.com]

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ for the Omani community**

*"وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا" - "And whoever fears Allah - He will make for him a way out" (Quran 65:2)*
