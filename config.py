"""
Voice-Only Omani Arabic Mental Health Chatbot
Configuration Management
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # AI Services (Optional for demo mode)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Azure Speech Services (Optional for demo mode)
    azure_speech_key: Optional[str] = Field(default=None, env="AZURE_SPEECH_KEY")
    azure_speech_region: str = Field(default="eastus", env="AZURE_SPEECH_REGION")
    
    # Application Settings
    app_name: str = Field(default="Omani Mental Health Assistant", env="APP_NAME")
    max_response_time: int = Field(default=15, env="MAX_RESPONSE_TIME")
    enable_crisis_detection: bool = Field(default=True, env="ENABLE_CRISIS_DETECTION")
    enable_logging: bool = Field(default=True, env="ENABLE_LOGGING")
    
    # Language & Cultural Settings
    primary_language: str = Field(default="ar-OM", env="PRIMARY_LANGUAGE")
    fallback_language: str = Field(default="ar-SA", env="FALLBACK_LANGUAGE")
    cultural_context: str = Field(default="gulf_arab", env="CULTURAL_CONTEXT")
    therapeutic_approach: str = Field(default="cbt_islamic", env="THERAPEUTIC_APPROACH")
    
    # Voice Settings
    tts_voice_female: str = Field(default="ar-OM-AyshaNeural", env="TTS_VOICE_FEMALE")
    tts_voice_male: str = Field(default="ar-OM-AbdullahNeural", env="TTS_VOICE_MALE")
    whisper_model: str = Field(default="base", env="WHISPER_MODEL")
    
    # Azure Deployment (Optional)
    azure_subscription_id: Optional[str] = Field(default=None, env="AZURE_SUBSCRIPTION_ID")
    azure_resource_group: str = Field(default="omani-mental-health-rg", env="AZURE_RESOURCE_GROUP")
    azure_app_name: str = Field(default="omani-mental-health-bot", env="AZURE_APP_NAME")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = Settings()

# Crisis keywords in Arabic and English
CRISIS_KEYWORDS_AR = [
    "انتحار", "اقتل نفسي", "أريد أن أموت", "لا أستطيع أكثر", 
    "سأنهي حياتي", "أفكر في الموت", "أريد أن أختفي"
]

CRISIS_KEYWORDS_EN = [
    "suicide", "kill myself", "want to die", "end my life", 
    "thinking about death", "want to disappear", "can't go on"
]

# Code-switching crisis patterns (Arabic-English mixed)
CRISIS_KEYWORDS_MIXED = [
    "I want to انتحار", "أريد أن أموت really", "لا أستطيع anymore", 
    "سأنهي my life", "thinking about الموت", "can't go on بعد اليوم",
    "want to die والله", "depression شديد", "feeling hopeless يا رب"
]

# Omani Arabic cultural context
OMANI_CULTURAL_PHRASES = {
    "greeting": "السلام عليكم، أهلاً وسهلاً بك",
    "comfort": "الله يعطيك العافية، أنا هنا لأساعدك",
    "encouragement": "إن شاء الله خير، كلها تعدي",
    "religious_comfort": "الله معك، وهذا ابتلاء وراه خير"
}

# Code-switching cultural phrases (common in Gulf Arabic)
OMANI_CODESWITCHING_PHRASES = {
    "greeting_mixed": "مرحبا! How are you اليوم؟",
    "comfort_mixed": "الله يعطيك العافية، I'm here to help you",
    "encouragement_mixed": "إن شاء الله it will be okay، كلها تعدي",
    "religious_comfort_mixed": "الله معك always، this is a test وراه خير",
    "support_mixed": "I understand أنك تمر بوقت صعب، but you're not alone",
    "validation_mixed": "Your feelings are valid والله، it's okay to feel this way",
    "hope_mixed": "There is hope دائماً، الله معك في كل خطوة"
}

# Common code-switching patterns in Gulf Arabic
CODESWITCHING_PATTERNS = {
    "time_expressions": ["today اليوم", "tomorrow بكرة", "now الحين", "later بعدين"],
    "feelings": ["happy مبسوط", "sad حزين", "stressed متوتر", "tired تعبان"],
    "family": ["my family أهلي", "my mom أمي", "my dad أبوي", "my kids عيالي"],
    "work": ["my work شغلي", "my job وظيفتي", "my boss المدير", "colleague زميل"],
    "common_phrases": ["wallah والله", "yalla يلا", "inshallah إن شاء الله", "mashallah ماشاء الله"],
    "transitions": ["بس but", "لكن however", "يعني I mean", "أو or"]
}

# Therapeutic techniques adapted for Islamic context
ISLAMIC_CBT_TECHNIQUES = {
    "dua_mindfulness": "التأمل والذكر",
    "gratitude_reflection": "تأمل النعم والحمد",
    "patience_building": "بناء الصبر والتوكل",
    "community_support": "الدعم المجتمعي والأسري"
}

# Code-switching therapeutic approaches
CODESWITCHING_CBT_TECHNIQUES = {
    "mindfulness_mixed": "Practice mindfulness مع الذكر والدعاء",
    "gratitude_mixed": "Count your blessings عد النعم daily",
    "patience_mixed": "Build sabr والتوكل على الله step by step",
    "support_mixed": "Seek help from family والأصدقاء والمجتمع"
}

# Emergency contacts for Oman
EMERGENCY_CONTACTS = {
    "police": "9999",
    "mental_health_hotline": "24673000",
    "ministry_of_health": "24602077"
} 