from flask import Blueprint, jsonify, request
import requests
import os
import json

chatbot_bp = Blueprint('chatbot', __name__)

# -----------------------------
# Simple Predefined Responses
# -----------------------------
SIMPLE_RESPONSES = {
    'hello': "Hello! I'm the FlashPress News AI assistant. How can I help you today?",
    'hi': "Hi there! What would you like to know about?",
    'how are you': "I'm functioning well, thank you! How can I help you?",
    'what is your name': "I'm the FlashPress News AI assistant, powered by advanced language models.",
    'who are you': "I'm an AI chatbot integrated into FlashPress News to help answer your questions.",
    'help': "I can help you with general questions, provide information, and have conversations. What would you like to know?",
    'bye': "Goodbye! Feel free to come back anytime you have questions.",
    'thank you': "You're welcome! Happy to help!",
    'thanks': "You're welcome! Let me know if you need anything else."
}

def get_simple_response(message):
    msg_lower = message.lower().strip()
    for key, resp in SIMPLE_RESPONSES.items():
        if key in msg_lower:
            return resp
    return None

# -----------------------------
# Main Chat Endpoint
# -----------------------------
@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()

        if not message:
            return jsonify({'success': False, 'error': 'No message provided'}), 400

        # 1️⃣ Simple predefined responses
        simple_response = get_simple_response(message)
        if simple_response:
            return jsonify({'success': True, 'response': simple_response})

        # 2️⃣ Hugging Face API call
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing Hugging Face API key'}), 500

        model_name = "gpt2"  # Change to your preferred model if needed
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {api_key}"}

        payload = {
            "inputs": message,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.9
            },
            "options": {"wait_for_model": True}
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                bot_response = extract_bot_response(result, message)
                if bot_response:
                    return jsonify({'success': True, 'response': bot_response})
            else:
                print(f"Hugging Face API returned status {response.status_code}: {response.text}")
        except requests.Timeout:
            print("Hugging Face request timed out.")
        except Exception as e:
            print(f"Hugging Face request error: {e}")

        # 3️⃣ Fallback response
        return jsonify({'success': True, 'response': generate_fallback_response(message)})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})


# -----------------------------
# Extract AI Response
# -----------------------------
def extract_bot_response(result, user_message):
    """
    Extracts generated text from HF model responses
    """
    text = ""
    if isinstance(result, list) and len(result) > 0:
        text = result[0].get("generated_text", "")
    elif isinstance(result, dict):
        text = result.get("generated_text", "")
    
    # Clean response
    text = text.replace("<|endoftext|>", "").strip()
    if text.lower().startswith(user_message.lower()):
        text = text[len(user_message):].strip()
    return text

# -----------------------------
# Fallback Responses
# -----------------------------
def generate_fallback_response(message):
    msg_lower = message.lower()
    if '?' in message:
        return "That's an interesting question! The AI models are currently loading. Could you try asking again or rephrase your question?"
    if 'news' in msg_lower:
        return "You can explore the latest news on our homepage!"
    if 'summarize' in msg_lower or 'summary' in msg_lower:
        return "You can use our AI Summarizer to get summaries of articles, YouTube videos, and PDFs."
    if 'fake' in msg_lower or 'real' in msg_lower or 'trust' in msg_lower:
        return "Use the Fake News Detector to verify if news sources are trustworthy."
    return "I'm here to help with FlashPress News. Could you rephrase your question or ask something else?"
