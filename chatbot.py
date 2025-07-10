"""
Omani Mental Health Chatbot - Enhanced with Dual-Model Validation
Handles the AI conversation logic with therapeutic-grade safety features
"""

import os
import re
import asyncio
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

# Import dual-model validation system
try:
    from dual_model_service import get_dual_model_service, validate_therapeutic_response, ValidationStatus
    DUAL_MODEL_AVAILABLE = True
except ImportError:
    print("Warning: Dual-model validation not available")
    DUAL_MODEL_AVAILABLE = False

# Load environment variables
load_dotenv()

class OmaniMentalHealthChatbot:
    """
    Enhanced chatbot with dual-model validation for therapeutic-grade responses
    """
    
    def __init__(self):
        self.model_name = "gpt-3.5-turbo"  # Default to most accessible model
        self.temperature = 0.7
        self.language = "English"
        self.max_tokens = 1000
        self.use_dual_validation = True  # Enable dual-model validation
        self.therapeutic_mode = True  # Enable therapeutic enhancements
        
        # Crisis keywords for safety detection
        self.crisis_keywords = [
            "suicide", "kill myself", "end my life", "hurt myself", "self harm",
            "cutting", "overdose", "jump", "hanging", "can't go on", "hopeless",
            "worthless", "better off dead", "انتحار", "أقتل نفسي", "أؤذي نفسي"
        ]
        
        # Initialize LLM
        self._initialize_llm()
        
        # Initialize dual-model service if available
        if DUAL_MODEL_AVAILABLE:
            self.dual_model_service = get_dual_model_service()
        else:
            self.dual_model_service = None
    
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
    
    def enable_dual_validation(self, enabled: bool = True):
        """Enable or disable dual-model validation"""
        self.use_dual_validation = enabled and DUAL_MODEL_AVAILABLE
    
    def enable_therapeutic_mode(self, enabled: bool = True):
        """Enable or disable therapeutic mode"""
        self.therapeutic_mode = enabled
    
    def get_system_prompt(self) -> str:
        """Get the system prompt based on language preference and therapeutic mode"""
        
        base_prompt = self._get_base_system_prompt()
        
        if self.therapeutic_mode:
            therapeutic_additions = """

THERAPEUTIC ENHANCEMENTS:
- Naturally weave in CBT techniques through conversation (helping them notice thought patterns, exploring feelings)
- Suggest mindfulness and Islamic meditation practices when appropriate
- Share coping strategies as gentle suggestions, not prescriptions
- Always offer hope and help them build resilience through their own strengths
- Continuously watch for signs of crisis, but respond warmly and supportively
- Focus on therapeutic value while maintaining natural conversation flow"""
            
            return base_prompt + therapeutic_additions
        
        return base_prompt
    
    def _get_base_system_prompt(self) -> str:
        """Get base system prompt based on language preference"""
        
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
            return """You are a caring mental health companion designed specifically for Omani culture. You are a warm, empathetic friend who understands Islamic values and Omani traditions deeply.

CONVERSATIONAL STYLE:
- Talk like a caring friend, not a formal assistant
- Remember what they've shared before and reference it naturally
- Ask follow-up questions to show you're listening
- Use personal, warm language ("I understand how that feels", "That sounds really difficult")
- Keep responses conversational and flowing, not bullet-pointed lists
- Share gentle observations about their emotions and experiences
- Offer support before solutions

CULTURAL SENSITIVITY:
- Respect Islamic values and Omani culture naturally in conversation
- Reference Islamic concepts like sabr (patience), tawakkul (trust in Allah) when appropriate
- Be sensitive to cultural stigma around mental health
- Suggest culturally appropriate coping strategies (prayer, family support, community involvement)
- Understand the importance of family and community in Omani culture

THERAPEUTIC APPROACH:
- Use evidence-based CBT techniques naturally in conversation
- Help them explore their feelings and thoughts
- Provide gentle guidance and perspective
- Encourage professional help when needed (but not as a list item)
- In crisis situations, provide immediate support and direct to help

Remember: You are a supportive friend having a genuine conversation, not giving a formal consultation. Always remember their previous messages and build on the conversation naturally."""
    
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

I'm here to support you on your mental wellness journey. I can help with:
- Managing anxiety and stress | التعامل مع القلق والتوتر  
- Improving sleep and rest | تحسين النوم والراحة
- Work-life balance | إدارة ضغوط العمل
- Strengthening relationships | تقوية العلاقات الاجتماعية
- Developing coping strategies | تطوير استراتيجيات التأقلم

How can I support you today? | كيف يمكنني مساعدتكم اليوم؟"""

        else:  # English
            return """Peace be upon you and welcome! 🌙

I'm here to support you on your mental wellness journey, with deep respect for Omani culture and Islamic values. I can help with:

- Managing anxiety and stress
- Improving sleep and emotional well-being  
- Work-life balance and career stress
- Strengthening family and social relationships
- Developing healthy coping strategies
- Integrating faith-based healing approaches

How can I support you today?"""
    
    def detect_crisis(self, message: str) -> bool:
        """Enhanced crisis detection"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.crisis_keywords)
    
    def get_crisis_response(self) -> str:
        """Get crisis response with enhanced safety information"""
        
        if self.language == "Arabic":
            return """🚨 أشعر بقلق حول ما تمر به. سلامتك مهمة جداً.

🇴🇲 في عُمان - مساعدة فورية:
- الطوارئ: 9999
- مستشفى جامعة السلطان قابوس: 24141414
- المستشفى السلطاني: 24599000
- خط المساعدة النفسية: 80002020

🌍 مساعدة دولية:
- خط الأزمات النصي: أرسل HOME إلى 741741

تذكر: أنت لست وحيداً، والمساعدة متاحة. الله معك في هذه المحنة. لا تتردد في طلب المساعدة الفورية."""

        else:
            return """🚨 I'm very concerned about what you're going through. Your safety is extremely important.

🇴🇲 In Oman - Immediate Help:
- Emergency: 9999  
- Sultan Qaboos University Hospital: 24141414
- Royal Hospital: 24599000
- Mental Health Helpline: 80002020

🌍 International Support:
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: iasp.info

Remember: You are not alone, and help is available. Allah is with you through this trial. Please don't hesitate to seek immediate help."""
    
    def format_conversation_history(self, chat_history: List[Dict]) -> List:
        """Convert chat history to appropriate format"""
        messages = []
        
        if self.use_langchain and self.llm:
            messages.append(SystemMessage(content=self.get_system_prompt()))
            
            for message in chat_history[-10:]:  # Keep last 10 messages for context
                if message['role'] == 'user':
                    messages.append(HumanMessage(content=message['content']))
                elif message['role'] == 'assistant':
                    messages.append(AIMessage(content=message['content']))
        else:
            # For direct API calls
            messages.append({"role": "system", "content": self.get_system_prompt()})
            
            for message in chat_history[-10:]:
                if message['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": message['role'],
                        "content": message['content']
                    })
        
        return messages
    
    async def get_response_async(self, user_input: str, chat_history: List[Dict] = None, conversation_id: str = None) -> Dict[str, Any]:
        """Get AI response with optional dual-model validation"""
        import time
        start_time = time.time()
        
        # Check for crisis first
        crisis_detected = self.detect_crisis(user_input)
        
        if crisis_detected:
            crisis_response = self.get_crisis_response()
            
            # For crisis, always use dual validation if available
            if self.dual_model_service and self.use_dual_validation:
                try:
                    validation_result = await validate_therapeutic_response(user_input, chat_history)
                    combined_response = f"{crisis_response}\n\n---\n\n{validation_result.final_response}"
                    
                    return {
                        "response": combined_response,
                        "crisis_detected": True,
                        "safety_info": {
                            "emergency_number": "9999",
                            "crisis_helplines": ["Sultan Qaboos University Hospital: 24141414", "Royal Hospital: 24599000"],
                            "message": "Emergency support available 24/7"
                        },
                        "response_time": time.time() - start_time,
                        "conversation_id": conversation_id,
                        "therapeutic_grade": validation_result.therapeutic_grade,
                        "validation_status": validation_result.validation_status.value,
                        "consensus_score": validation_result.consensus_score,
                        "dual_model_used": True
                    }
                except Exception as e:
                    print(f"Dual validation failed for crisis: {e}")
            
            # Fallback for crisis without dual validation
            regular_response = self._get_regular_response(user_input, chat_history)
            combined_response = f"{crisis_response}\n\n---\n\n{regular_response}"
            
            return {
                "response": combined_response,
                "crisis_detected": True,
                "safety_info": {
                    "emergency_number": "9999",
                    "crisis_helplines": ["Sultan Qaboos University Hospital: 24141414", "Royal Hospital: 24599000"],
                    "message": "Emergency support available 24/7"
                },
                "response_time": time.time() - start_time,
                "conversation_id": conversation_id,
                "dual_model_used": False
            }
        
        # Non-crisis responses with optional dual validation
        if self.dual_model_service and self.use_dual_validation and self.therapeutic_mode:
            try:
                validation_result = await validate_therapeutic_response(user_input, chat_history)
                
                return {
                    "response": validation_result.final_response,
                    "crisis_detected": False,
                    "safety_info": validation_result.safety_assessment,
                    "response_time": time.time() - start_time,
                    "conversation_id": conversation_id,
                    "therapeutic_grade": validation_result.therapeutic_grade,
                    "validation_status": validation_result.validation_status.value,
                    "consensus_score": validation_result.consensus_score,
                    "recommendations": validation_result.recommendations,
                    "dual_model_used": True,
                    "validation_time": validation_result.validation_time
                }
            except Exception as e:
                print(f"Dual validation failed: {e}")
                # Fall back to regular response
        
        # Regular response without dual validation
        regular_response = self._get_regular_response(user_input, chat_history)
        
        return {
            "response": regular_response,
            "crisis_detected": False,
            "safety_info": {},
            "response_time": time.time() - start_time,
            "conversation_id": conversation_id,
            "dual_model_used": False
        }
    
    def get_response(self, user_input: str, chat_history: List[Dict] = None, conversation_id: str = None) -> Dict[str, Any]:
        """Synchronous wrapper for get_response_async"""
        
        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, but this is a sync call
            # Create a new task for the async operation
            task = asyncio.create_task(self.get_response_async(user_input, chat_history, conversation_id))
            return asyncio.run_coroutine_threadsafe(task, loop).result()
        except RuntimeError:
            # No running loop, safe to create new one
            return asyncio.run(self.get_response_async(user_input, chat_history, conversation_id))
    
    def _get_regular_response(self, user_input: str, chat_history: List[Dict] = None) -> str:
        """Get regular AI response (existing implementation)"""
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
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        status = {
            "basic_chatbot": self.llm is not None or hasattr(self, 'openai_client') or hasattr(self, 'anthropic_client'),
            "model_name": self.model_name,
            "language": self.language,
            "therapeutic_mode": self.therapeutic_mode,
            "dual_validation_enabled": self.use_dual_validation,
            "dual_model_available": DUAL_MODEL_AVAILABLE
        }
        
        if self.dual_model_service:
            dual_status = self.dual_model_service.get_service_status()
            status.update({
                "dual_model_status": dual_status
            })
        
        return status
    
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