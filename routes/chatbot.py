# chatbot.py
import os
import requests

# -------------------- CONFIG --------------------
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
CHAT_MODEL = "deepseek-ai/DeepSeek-R1:fireworks-ai"
BASE_URL = "https://router.huggingface.co/v1"

# -------------------- CHAT FUNCTION --------------------
def chat_with_ai(message: str, context: str = None) -> str:
    """
    Sends a message to the DeepSeek-R1 chatbot and returns the AI response.
    The system prompt forces the bot to always give clear, concise, news-related answers.
    """
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are a professional news assistant. "
        "Always respond with accurate, clear, concise answers about news, "
        "without generic fallback messages. "
        "Do not say 'I'm still learning' or similar phrases."
    )

    user_content = f"Context: {context}\nUser: {message}" if context else message

    payload = {
        "model": CHAT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip() \
            or "AI returned an empty response."
    except requests.exceptions.RequestException as e:
        print("Chat error:", e)
        return "AI chat model unavailable. Check your API key or network connection."

# -------------------- TEST --------------------
if __name__ == "__main__":
    print("FlashPress News Chatbot")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Bot: Goodbye!")
            break
        reply = chat_with_ai(user_input)
        print("Bot:", reply)
