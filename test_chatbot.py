"""
Test script for Omani Mental Health Chatbot
Run this to verify the setup is working correctly
"""

import os
from dotenv import load_dotenv
from chatbot import OmaniMentalHealthBot

def test_environment():
    """Test if environment variables are properly set"""
    print("🔧 Testing Environment Setup...")
    
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not found or not set properly")
        print("   Please set OPENAI_API_KEY in your .env file")
        return False
    else:
        print("✅ OpenAI API key found")
    
    if not anthropic_key or anthropic_key == "your_anthropic_api_key_here":
        print("⚠️  Anthropic API key not found (optional)")
        print("   Set ANTHROPIC_API_KEY in .env file to use Claude models")
    else:
        print("✅ Anthropic API key found")
    
    return True

def test_chatbot_initialization():
    """Test if chatbot can be initialized"""
    print("\n🤖 Testing Chatbot Initialization...")
    
    try:
        bot = OmaniMentalHealthBot()
        print("✅ Chatbot initialized successfully")
        return bot
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")
        return None

def test_basic_functionality(bot):
    """Test basic chatbot functionality"""
    print("\n💬 Testing Basic Functionality...")
    
    # Test welcome message
    try:
        welcome = bot.get_welcome_message()
        print("✅ Welcome message generated successfully")
        print(f"   Preview: {welcome[:100]}...")
    except Exception as e:
        print(f"❌ Failed to generate welcome message: {str(e)}")
        return False
    
    # Test crisis detection
    try:
        crisis_test = bot.detect_crisis("I feel hopeless and want to hurt myself")
        if crisis_test:
            print("✅ Crisis detection working correctly")
        else:
            print("⚠️  Crisis detection may not be working properly")
    except Exception as e:
        print(f"❌ Crisis detection failed: {str(e)}")
    
    # Test simple response
    try:
        response = bot.get_response("Hello, I'm feeling a bit anxious today.")
        print("✅ Basic response generation working")
        print(f"   Preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Failed to generate response: {str(e)}")
        return False

def test_language_switching(bot):
    """Test language switching functionality"""
    print("\n🌍 Testing Language Support...")
    
    languages = ["English", "Arabic", "Both / كلاهما"]
    
    for lang in languages:
        try:
            bot.set_language(lang)
            welcome = bot.get_welcome_message()
            print(f"✅ {lang} language support working")
        except Exception as e:
            print(f"❌ {lang} language support failed: {str(e)}")

def test_model_switching(bot):
    """Test model switching functionality"""
    print("\n🔄 Testing Model Switching...")
    
    models = ["gpt-3.5-turbo", "gpt-4"]
    
    for model in models:
        try:
            bot.set_model(model)
            print(f"✅ {model} model set successfully")
            
            # Test a simple response to verify the model works
            if model == "gpt-4":
                # Try GPT-4 but expect it might fail
                try:
                    test_response = bot.get_response("Hello, can you respond briefly?")
                    print(f"✅ {model} is accessible and working")
                except Exception as e:
                    if "model_not_found" in str(e) or "does not have access" in str(e):
                        print(f"⚠️  {model} not accessible (expected), fallback should work")
                    else:
                        print(f"❌ Unexpected error with {model}: {str(e)}")
            else:
                # GPT-3.5-turbo should always work
                test_response = bot.get_response("Hello, can you respond briefly?")
                print(f"✅ {model} response generated successfully")
                
        except Exception as e:
            print(f"❌ Failed to set {model}: {str(e)}")

def main():
    """Run all tests"""
    print("🧠 Omani Mental Health Chatbot - Test Suite")
    print("=" * 50)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed. Please fix configuration before proceeding.")
        return
    
    # Test chatbot initialization
    bot = test_chatbot_initialization()
    if not bot:
        print("\n❌ Chatbot initialization failed. Check your API keys and try again.")
        return
    
    # Test basic functionality
    if not test_basic_functionality(bot):
        print("\n❌ Basic functionality test failed.")
        return
    
    # Test language switching
    test_language_switching(bot)
    
    # Test model switching
    test_model_switching(bot)
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\n📋 Next Steps:")
    print("1. Run 'streamlit run app.py' to start the application")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Test the full interface and functionality")
    print("4. Deploy to Azure when ready!")

if __name__ == "__main__":
    main() 