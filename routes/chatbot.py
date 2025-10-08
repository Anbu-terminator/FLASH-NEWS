from flask import Blueprint, jsonify, request
import requests
import os

chatbot_bp = Blueprint('chatbot', __name__)

# ---------------------------
# Simple rule-based responses
# ---------------------------
SIMPLE_RESPONSES = {
    'hello': "Hello! I'm the FlashPress News AI assistant. How can I help you today?",
    'hi': "Hi there! What would you like to know about?",
    'how are you': "I'm functioning well, thank you! How are you doing?",
    'what is your name': "I'm the FlashPress News AI assistant, built to help you explore and understand the news.",
    'who are you': "I'm an AI chatbot integrated into FlashPress News to help answer your questions.",
    'help': "I can answer general questions, summarize news, and help you explore stories. What would you like to do?",
    'bye': "Goodbye! Have a great day — and come back soon for the latest updates!",
    'thank you': "You're very welcome! 😊",
    'thanks': "You're very welcome! 😊"
}

def get_simple_response(message):
    msg = message.lower().strip()
    for key, resp in SIMPLE_RESPONSES.items():
        if key in msg:
            return resp
    return None

# ---------------------------
# Chat Endpoint
# ---------------------------
@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        # 1️⃣ Check for simple static responses
        simple_response = get_simple_response(message)
        if simple_response:
            return jsonify({'success': True, 'response': simple_response})

        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing Hugging Face API key'}), 500

        # 2️⃣ Use a reliable conversational model
        model_name = "facebook/blenderbot-400M-distill"
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": message,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.8,
                "top_p": 0.9
            },
            "options": {"wait_for_model": True}
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)

        if response.status_code == 200:
            result = response.json()

            # Handle both list and dict responses
            bot_response = None
            if isinstance(result, list) and len(result) > 0:
                bot_response = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                bot_response = result.get('generated_text', result.get('summary', ''))

            if bot_response:
                # Clean unwanted parts
                bot_response = bot_response.replace('<|endoftext|>', '').strip()
                # Avoid echoing back the user message
                if bot_response.lower().startswith(message.lower()):
                    bot_response = bot_response[len(message):].strip()

                # Ensure valid reply
                if len(bot_response) > 2:
                    return jsonify({'success': True, 'response': bot_response})

        # 3️⃣ If API didn’t return valid output → Fallback
        return jsonify({'success': True, 'response': generate_fallback_response(message)})

    except requests.Timeout:
        return jsonify({'success': False, 'error': 'The model took too long to respond. Please try again.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})

# ---------------------------
# Fallback intelligent responses
# ---------------------------
def generate_fallback_response(message):
    msg_lower = message.lower()

    # If it's a question
    if '?' in message:
        return "That's a great question! Unfortunately, my AI model didn't respond just now. Please rephrase or try again in a few seconds."

    # Topic-based fallback
    if 'news' in msg_lower:
        return "You can explore the latest verified news stories on our homepage!"
    if 'summarize' in msg_lower or 'summary' in msg_lower:
        return "Try our Summarizer page — it can summarize articles, YouTube videos, and PDFs for you!"
    if 'fake' in msg_lower or 'real' in msg_lower or 'trust' in msg_lower:
        return "Our Fake News Detector can help verify the authenticity of any article."

    # Generic fallback
    return "I'm not sure I understood that, but I'm here to help you with FlashPress News content or questions!"
