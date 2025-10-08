from flask import Blueprint, jsonify, request
import requests
import os

chatbot_bp = Blueprint('chatbot', __name__)

# -----------------------------------------
# Basic Predefined Responses for Common Input
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

        # 1️⃣ Simple Response Check
        simple_response = get_simple_response(message)
        if simple_response:
            return jsonify({'success': True, 'response': simple_response})

        # 2️⃣ API Setup
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing Hugging Face API key'}), 500

        # Models to try — both reliable conversational models
        models_to_try = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill"
        ]

        headers = {"Authorization": f"Bearer {api_key}"}

        # 3️⃣ Try Multiple Models until one succeeds
        for model_name in models_to_try:
            API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

            payload = {
                "inputs": message,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "repetition_penalty": 1.1
                },
                "options": {"wait_for_model": True}
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    bot_response = extract_bot_response(result, message)

                    if bot_response and len(bot_response) > 3:
                        return jsonify({'success': True, 'response': bot_response})

                elif response.status_code == 503:
                    # Model still loading, try next one
                    continue

            except requests.Timeout:
                continue
            except Exception:
                continue

        # 4️⃣ Fallback if both models fail
        return jsonify({'success': True, 'response': generate_fallback_response(message)})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'})


# -----------------------------------------
# Extract AI Response from HF JSON
# -----------------------------------------
def extract_bot_response(result, user_message):
    """
    Safely extracts the generated text from various Hugging Face model formats
    """
    if isinstance(result, list) and len(result) > 0:
        if "generated_text" in result[0]:
            text = result[0]["generated_text"]
        elif "text" in result[0]:
            text = result[0]["text"]
        else:
            text = ""
    elif isinstance(result, dict):
        text = result.get("generated_text", result.get("text", ""))
    else:
        text = ""

    # Clean response
    text = text.replace("<|endoftext|>", "").strip()

    # Remove user echo if present
    if text.lower().startswith(user_message.lower()):
        text = text[len(user_message):].strip()

    return text


# -----------------------------------------
# Fallback Smart Responses
# -----------------------------------------
def generate_fallback_response(message):
    msg_lower = message.lower()

    # Question-based
    if '?' in message:
        return "That's a good question! Could you please try again in a moment? The AI might be reconnecting."

    # Topic-based
    if 'news' in msg_lower:
        return "You can explore the latest verified stories right on FlashPress News!"
    if 'summarize' in msg_lower or 'summary' in msg_lower:
        return "Try our AI Summarizer — it can summarize articles, PDFs, and even YouTube videos."
    if 'fake' in msg_lower or 'real' in msg_lower or 'trust' in msg_lower:
        return "Use the Fake News Detector to check if a story is authentic."

    # Default friendly fallback
    return "I'm still learning from the latest FlashPress data! Could you rephrase your question or ask about something else?"
