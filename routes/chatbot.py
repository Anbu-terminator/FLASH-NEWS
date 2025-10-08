from flask import Blueprint, jsonify, request
import requests
import os

chatbot_bp = Blueprint('chatbot', __name__)

# -----------------------------------------
# Basic predefined responses for common input
# -----------------------------------------
SIMPLE_RESPONSES = {
    'hello': "Hello! I'm the FlashPress News AI assistant. How can I help you today?",
    'hi': "Hi there! What would you like to talk about?",
    'how are you': "I'm doing great, thank you for asking! How about you?",
    'what is your name': "I'm the FlashPress News AI assistant — your personal news helper.",
    'who are you': "I'm an AI chatbot integrated into FlashPress News to answer your questions and provide insights.",
    'help': "I can chat with you, summarize news, or explain topics. What would you like to do?",
    'bye': "Goodbye! Have a great day, and come back soon for the latest updates!",
    'thank you': "You're welcome! 😊",
    'thanks': "You're welcome! 😊"
}


def get_simple_response(message):
    msg = message.lower().strip()
    for key, resp in SIMPLE_RESPONSES.items():
        if key in msg:
            return resp
    return None


# -----------------------------------------
# Main Chat Endpoint
# -----------------------------------------
@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        # 1️⃣ Check for simple responses first
        simple_response = get_simple_response(message)
        if simple_response:
            return jsonify({'success': True, 'response': simple_response})

        # 2️⃣ Get Hugging Face API Key
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing Hugging Face API key'}), 500

        # 3️⃣ Use a reliable conversational model
        model_name = "microsoft/DialoGPT-medium"
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "inputs": {
                "text": message
            },
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.1
            },
            "options": {"wait_for_model": True}
        }

        # 4️⃣ Make API call
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)

        # 5️⃣ Parse response
        if response.status_code == 200:
            result = response.json()
            bot_response = None

            if isinstance(result, list) and len(result) > 0:
                bot_response = result[0].get('generated_text', '')
            elif isinstance(result, dict):
                bot_response = result.get('generated_text', result.get('summary', ''))

            if bot_response:
                bot_response = bot_response.replace('<|endoftext|>', '').strip()

                # Prevent echoing user message
                if bot_response.lower().startswith(message.lower()):
                    bot_response = bot_response[len(message):].strip()

                if len(bot_response) > 3:
                    return jsonify({'success': True, 'response': bot_response})

        # 6️⃣ Fallback intelligent response
        return jsonify({'success': True, 'response': generate_fallback_response(message)})

    except requests.Timeout:
        return jsonify({'success': False, 'error': 'The model took too long to respond. Please try again.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})


# -----------------------------------------
# Fallback Response (when model is slow/offline)
# -----------------------------------------
def generate_fallback_response(message):
    msg_lower = message.lower()

    # Handle question forms
    if '?' in message:
        return "That's a great question! Please try again in a moment — my AI engine is reconnecting."

    # Topic-based guidance
    if 'news' in msg_lower:
        return "You can browse the latest verified stories right on FlashPress News!"
    if 'summarize' in msg_lower or 'summary' in msg_lower:
        return "Try our AI Summarizer — it can summarize articles, PDFs, and even YouTube videos."
    if 'fake' in msg_lower or 'real' in msg_lower or 'trust' in msg_lower:
        return "You can use the Fake News Detector to verify if a story is authentic."

    # Default fallback
    return "I'm here to chat about the latest news and updates! Could you rephrase or ask something else?"
