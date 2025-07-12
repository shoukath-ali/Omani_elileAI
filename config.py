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

# Omani Arabic cultural context
OMANI_CULTURAL_PHRASES = {
    "greeting": "السلام عليكم، أهلاً وسهلاً بك",
    "comfort": "الله يعطيك العافية، أنا هنا لأساعدك",
    "encouragement": "إن شاء الله خير، كلها تعدي",
    "religious_comfort": "الله معك، وهذا ابتلاء وراه خير"
}

# Therapeutic techniques adapted for Islamic context
ISLAMIC_CBT_TECHNIQUES = {
    "dua_mindfulness": "التأمل والذكر",
    "gratitude_reflection": "تأمل النعم والحمد",
    "patience_building": "بناء الصبر والتوكل",
    "community_support": "الدعم المجتمعي والأسري"
}

# Emergency contacts for Oman
EMERGENCY_CONTACTS = {
    "police": "9999",
    "mental_health_hotline": "24673000",
    "ministry_of_health": "24602077"
} 