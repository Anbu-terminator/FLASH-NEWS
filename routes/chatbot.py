from flask import Blueprint, jsonify, request
import requests
import os

chatbot_bp = Blueprint('chatbot', __name__)

# Simple rule-based responses for common queries
SIMPLE_RESPONSES = {
    'hello': "Hello! I'm the FlashPress News AI assistant. How can I help you today?",
    'hi': "Hi there! What would you like to know about?",
    'how are you': "I'm functioning well, thank you! I'm here to help answer your questions.",
    'what is your name': "I'm the FlashPress News AI assistant, powered by advanced language models.",
    'who are you': "I'm an AI chatbot integrated into FlashPress News to help answer your questions.",
    'help': "I can help you with general questions, provide information, and have conversations. What would you like to know?",
    'bye': "Goodbye! Feel free to come back anytime you have questions.",
    'thank you': "You're welcome! Happy to help!",
    'thanks': "You're welcome! Let me know if you need anything else."
}

def get_simple_response(message):
    """Check if message matches simple patterns"""
    msg_lower = message.lower().strip()
    
    for key, response in SIMPLE_RESPONSES.items():
        if key in msg_lower:
            return response
    
    return None

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        # First check for simple responses
        simple_response = get_simple_response(message)
        if simple_response:
            return jsonify({'success': True, 'response': simple_response})
        
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # Try AI models with shorter timeout for faster response
        models_to_try = [
            ("deepseek-ai/DeepSeek-R1", 250, 0.7),  # DeepSeek-R1
            ("microsoft/DialoGPT-medium", 150, 0.8),  # DialoGPT
            ("facebook/blenderbot-400M-distill", 150, 0.8),  # BlenderBot
            ("google/flan-t5-base", 100, 0.7)  # FLAN-T5
        ]
        
        for model_name, max_tokens, temp in models_to_try:
            try:
                API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
                headers = {"Authorization": f"Bearer {api_key}"}
                
                payload = {
                    "inputs": message,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": temp,
                        "top_p": 0.9,
                        "return_full_text": False
                    },
                    "options": {"wait_for_model": True, "use_cache": False}
                }
                
                response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract response from different formats
                    bot_response = None
                    
                    if isinstance(result, list) and len(result) > 0:
                        bot_response = result[0].get('generated_text', '')
                    elif isinstance(result, dict):
                        bot_response = result.get('generated_text', result.get('summary', ''))
                    
                    # Clean up response
                    if bot_response:
                        # Remove input echo if present
                        if bot_response.startswith(message):
                            bot_response = bot_response[len(message):].strip()
                        
                        # Remove common artifacts
                        bot_response = bot_response.replace('<|endoftext|>', '').strip()
                        
                        if bot_response and len(bot_response) > 3:
                            return jsonify({'success': True, 'response': bot_response})
                
            except requests.Timeout:
                continue
            except Exception:
                continue
        
        # Fallback: Generate a contextual response
        fallback_response = generate_fallback_response(message)
        return jsonify({'success': True, 'response': fallback_response})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

def generate_fallback_response(message):
    """Generate intelligent fallback responses"""
    msg_lower = message.lower()
    
    # Question detection
    if '?' in message:
        if 'what' in msg_lower or 'how' in msg_lower or 'why' in msg_lower or 'when' in msg_lower or 'where' in msg_lower or 'who' in msg_lower:
            return f"That's an interesting question about {message.split('?')[0].split()[-3:]}. The AI models are currently loading. Could you try asking again in a moment, or rephrase your question?"
    
    # Topic-specific responses
    if 'news' in msg_lower:
        return "You can explore the latest news on our homepage! The AI models are loading right now, but feel free to browse the news feed."
    
    if 'summarize' in msg_lower or 'summary' in msg_lower:
        return "You can use our AI Summarizer to get summaries of articles, YouTube videos, and PDFs! Check out the Summarizer page."
    
    if 'fake' in msg_lower or 'real' in msg_lower or 'trust' in msg_lower:
        return "Use our Fake News Detector to verify if news sources are trustworthy! It checks against 50+ trusted sources."
    
    # Default contextual response
    return f"I understand you mentioned something about '{message[:50]}...' The AI models are warming up. Please try again in a few moments, or I can help you navigate to our news features!"
