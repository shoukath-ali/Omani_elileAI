"""
Omani Mental Health Chatbot - LangChain Backend
Handles the AI conversation logic with safety features
"""

import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Try importing LangChain components with fallbacks
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    print("Warning: langchain_openai not available, using direct OpenAI API")
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    print("Warning: langchain_anthropic not available")
    ChatAnthropic = None

try:
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
except ImportError:
    # Fallback for basic message structure
    class BaseMessage:
        def __init__(self, content: str):
            self.content = content
    
    class HumanMessage(BaseMessage):
        pass
    
    class AIMessage(BaseMessage):
        pass
    
    class SystemMessage(BaseMessage):
        pass

# Direct API imports as fallback
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

# Load environment variables
load_dotenv()

class OmaniMentalHealthBot:
    """
    Main chatbot class with mental health focus and Omani cultural context
    """
    
    def __init__(self):
        self.model_name = "gpt-3.5-turbo"  # Default to most accessible model
        self.temperature = 0.7
        self.language = "English"
        self.max_tokens = 1000
        
        # Crisis keywords for safety detection
        self.crisis_keywords = [
            "suicide", "kill myself", "end my life", "hurt myself", "self harm",
            "cutting", "overdose", "jump", "hanging", "can't go on", "hopeless",
            "worthless", "better off dead", "انتحار", "أقتل نفسي", "أؤذي نفسي"
        ]
        
        # Initialize LLM
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model based on current settings"""
        try:
            if "gpt" in self.model_name.lower() and ChatOpenAI:
                # Use LangChain if available
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
                self.use_langchain = True
            elif "claude" in self.model_name.lower() and ChatAnthropic:
                # Use LangChain if available
                self.llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                self.use_langchain = True
            elif openai and "gpt" in self.model_name.lower():
                # Fallback to direct OpenAI API
                self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.llm = None  # Will use direct API calls
                self.use_langchain = False
                print("Using direct OpenAI API (LangChain not available)")
            elif anthropic and "claude" in self.model_name.lower():
                # Fallback to direct Anthropic API
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                self.llm = None  # Will use direct API calls
                self.use_langchain = False
                print("Using direct Anthropic API (LangChain not available)")
            else:
                # Basic fallback
                self.llm = None
                self.use_langchain = False
                print("Warning: No AI service available, using fallback responses")
        except Exception as e:
            self.llm = None
            self.use_langchain = False
            print(f"Warning: Failed to initialize AI service: {str(e)}")
            print("Using fallback responses")
    
    def set_model(self, model_name: str):
        """Set the AI model"""
        self.model_name = model_name
        self._initialize_llm()
    
    def set_temperature(self, temperature: float):
        """Set the creativity level"""
        self.temperature = temperature
        self._initialize_llm()
    
    def set_language(self, language: str):
        """Set the preferred language"""
        self.language = language
    
    def get_system_prompt(self) -> str:
        """Get the system prompt based on language preference"""
        
        if self.language == "Arabic":
            return """أنت مساعد للصحة النفسية مصمم خصيصاً للثقافة العُمانية. أنت متعاطف ومتفهم ومحترم للقيم الإسلامية والتقاليد العُمانية.

إرشاداتك:
- كن دافئاً ومتعاطفاً في جميع الردود
- احترم القيم الإسلامية والثقافة العُمانية
- قدم نصائح عملية للصحة النفسية
- شجع طلب المساعدة المهنية عند الحاجة
- لا تقدم تشخيصات طبية
- في حالات الأزمات، وجه للمساعدة الفورية

تذكر: أنت مساعد للدعم العاطفي وليس بديلاً للرعاية الطبية المهنية."""

        elif self.language == "Both / كلاهما":
            return """You are a mental health support assistant designed for Omani culture. You are empathetic, understanding, and respectful of Islamic values and Omani traditions. Respond in both English and Arabic.

أنت مساعد للصحة النفسية مصمم للثقافة العُمانية. كن متعاطفاً ومتفهماً ومحترماً للقيم الإسلامية والتقاليد العُمانية.

Your guidelines:
- Be warm and empathetic in all responses
- Respect Islamic values and Omani culture  
- Provide practical mental health advice
- Encourage seeking professional help when needed
- Do not provide medical diagnoses
- In crisis situations, direct to immediate help

Remember: You are a supportive companion, not a replacement for professional medical care."""

        else:  # English
            return """You are a mental health support assistant designed specifically for Omani culture. You are empathetic, understanding, and respectful of Islamic values and Omani traditions.

Your guidelines:
- Be warm and empathetic in all responses
- Respect Islamic values and Omani culture
- Provide practical mental health advice rooted in both modern psychology and Islamic teachings
- Encourage seeking professional help when needed
- Do not provide medical diagnoses
- In crisis situations, direct to immediate help
- Reference Islamic concepts like sabr (patience), tawakkul (trust in Allah), and community support when appropriate
- Be sensitive to cultural stigma around mental health
- Suggest culturally appropriate coping strategies (prayer, family support, community involvement)

Remember: You are a supportive companion, not a replacement for professional medical care."""
    
    def get_welcome_message(self) -> str:
        """Get a culturally appropriate welcome message"""
        
        if self.language == "Arabic":
            return """السلام عليكم ومرحباً بكم 🌙

أنا هنا لدعمكم في رحلة الصحة النفسية. يمكنني مساعدتكم في:
- التعامل مع القلق والتوتر
- تحسين النوم والراحة
- إدارة ضغوط العمل
- تقوية العلاقات الاجتماعية
- تطوير استراتيجيات التأقلم

كيف يمكنني مساعدتكم اليوم؟"""

        elif self.language == "Both / كلاهما":
            return """Peace be upon you and welcome! السلام عليكم ومرحباً بكم 🌙

I'm here to support you on your mental wellness journey. أنا هنا لدعمكم في رحلة الصحة النفسية.

I can help with:
- Managing anxiety and stress / التعامل مع القلق والتوتر
- Improving sleep and rest / تحسين النوم والراحة  
- Work-life balance / التوازن بين العمل والحياة
- Building stronger relationships / تقوية العلاقات
- Developing coping strategies / تطوير استراتيجيات التأقلم

How can I support you today? كيف يمكنني مساعدتكم اليوم؟"""

        else:  # English
            return """Peace be upon you and welcome! 🌙

I'm here to support you on your mental wellness journey with understanding of Omani culture and Islamic values.

I can help you with:
- Managing anxiety and stress
- Improving sleep and relaxation
- Work-life balance
- Building stronger relationships
- Developing healthy coping strategies
- Navigating life transitions
- Building resilience through faith and community

How can I support you today? Feel free to share what's on your mind."""
    
    def detect_crisis(self, message: str) -> bool:
        """Detect potential crisis situations"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.crisis_keywords)
    
    def get_crisis_response(self) -> str:
        """Get appropriate crisis response based on language"""
        
        if self.language == "Arabic":
            return """🚨 أشعر بقلق حول ما تمر به. سلامتك مهمة جداً.

🇴🇲 في عُمان:
- الطوارئ: 9999
- مستشفى جامعة السلطان قابوس: 24141414
- المستشفى السلطاني: 24599000

🌍 مساعدة دولية:
- خط الأزمات النصي: أرسل HOME إلى 741741

تذكر: أنت لست وحيداً، والمساعدة متاحة. الله معك في هذه المحنة."""

        else:
            return """🚨 I'm concerned about what you're going through. Your safety is very important.

🇴🇲 In Oman:
- Emergency: 9999  
- Sultan Qaboos University Hospital: 24141414
- Royal Hospital: 24599000

🌍 International:
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: iasp.info

Remember: You are not alone, and help is available. Allah is with you through this trial."""
    
    def format_conversation_history(self, chat_history: List[Dict]) -> List:
        """Convert chat history to LangChain format"""
        messages = [SystemMessage(content=self.get_system_prompt())]
        
        for message in chat_history[-10:]:  # Keep last 10 messages for context
            if message['role'] == 'user':
                messages.append(HumanMessage(content=message['content']))
            elif message['role'] == 'assistant':
                messages.append(AIMessage(content=message['content']))
        
        return messages
    
    def get_response(self, user_input: str, chat_history: List[Dict] = None) -> str:
        """Get AI response to user input"""
        
        # Check for crisis first
        if self.detect_crisis(user_input):
            crisis_response = self.get_crisis_response()
            regular_response = self._get_regular_response(user_input, chat_history)
            return f"{crisis_response}\n\n---\n\n{regular_response}"
        
        return self._get_regular_response(user_input, chat_history)
    
    def _get_regular_response(self, user_input: str, chat_history: List[Dict] = None) -> str:
        """Get regular AI response"""
        try:
            if self.use_langchain and self.llm:
                # Use LangChain approach
                if chat_history:
                    messages = self.format_conversation_history(chat_history)
                else:
                    messages = [SystemMessage(content=self.get_system_prompt())]
                
                # Add current user message
                messages.append(HumanMessage(content=user_input))
                
                # Get response from LLM
                response = self.llm(messages)
                
                # Extract content based on response type
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
            
            elif not self.use_langchain and hasattr(self, 'openai_client') and "gpt" in self.model_name.lower():
                # Direct OpenAI API call (v1.0+ format)
                messages = [
                    {"role": "system", "content": self.get_system_prompt()},
                ]
                
                # Add chat history
                if chat_history:
                    for msg in chat_history[-10:]:  # Last 10 messages
                        if msg['role'] in ['user', 'assistant']:
                            messages.append({
                                "role": msg['role'],
                                "content": msg['content']
                            })
                
                # Add current message
                messages.append({"role": "user", "content": user_input})
                
                # Make API call with fallback
                try:
                    response = self.openai_client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                    return response.choices[0].message.content
                    
                except Exception as model_error:
                    # Check if it's a model access error
                    if "model_not_found" in str(model_error) or "does not have access" in str(model_error):
                        print(f"Model {self.model_name} not accessible, falling back to gpt-3.5-turbo")
                        # Fallback to gpt-3.5-turbo
                        response = self.openai_client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens
                        )
                        # Update the model for future calls
                        self.model_name = "gpt-3.5-turbo"
                        return response.choices[0].message.content
                    else:
                        raise model_error
            
            elif not self.use_langchain and hasattr(self, 'anthropic_client') and "claude" in self.model_name.lower():
                # Direct Anthropic API call
                system_prompt = self.get_system_prompt()
                
                # Format conversation for Anthropic
                conversation = ""
                if chat_history:
                    for msg in chat_history[-10:]:  # Last 10 messages
                        if msg['role'] == 'user':
                            conversation += f"Human: {msg['content']}\n\n"
                        elif msg['role'] == 'assistant':
                            conversation += f"Assistant: {msg['content']}\n\n"
                
                conversation += f"Human: {user_input}\n\nAssistant:"
                
                # Make API call
                response = self.anthropic_client.completions.create(
                    model=self.model_name,
                    prompt=f"{system_prompt}\n\n{conversation}",
                    temperature=self.temperature,
                    max_tokens_to_sample=self.max_tokens
                )
                
                return response.completion.strip()
            
            else:
                # Fallback response when no AI service is available
                return self._get_fallback_response("No AI service initialized")
                
        except Exception as e:
            return self._get_fallback_response(str(e))
    
    def _get_fallback_response(self, error: str) -> str:
        """Provide a helpful fallback response when AI fails"""
        
        if self.language == "Arabic":
            return """أعتذر، أواجه صعوبة تقنية في الوقت الحالي. 

في هذه الأثناء، إليك بعض النصائح المفيدة:
- خذ نفساً عميقاً واسترخِ
- تذكر أن المشاكل مؤقتة
- تواصل مع أحبائك
- اطلب المساعدة المهنية إذا كنت بحاجة لها

سأحاول مساعدتك مرة أخرى قريباً."""

        else:
            return f"""I apologize, but I'm experiencing a technical difficulty right now. 

In the meantime, here are some helpful reminders:
- Take a deep breath and try to relax
- Remember that difficult times are temporary  
- Reach out to loved ones for support
- Consider professional help if you need it
- Practice self-care and be patient with yourself

I'll try to help you again soon. Error details: {error}"""
    
    def get_mental_health_tips(self) -> List[str]:
        """Get general mental health tips"""
        
        if self.language == "Arabic":
            return [
                "مارس الصلاة والذكر للراحة النفسية",
                "احتفظ بروتين يومي منتظم",
                "مارس الرياضة بانتظام",
                "تواصل مع الأهل والأصدقاء",
                "احصل على نوم كافٍ",
                "تناول طعاماً صحياً",
                "مارس الامتنان والتأمل"
            ]
        else:
            return [
                "Practice regular prayer and dhikr for spiritual peace",
                "Maintain a consistent daily routine",
                "Engage in regular physical exercise",
                "Stay connected with family and friends",
                "Get adequate sleep (7-9 hours)",
                "Eat nutritious, balanced meals",
                "Practice gratitude and mindfulness",
                "Seek professional help when needed"
            ] 