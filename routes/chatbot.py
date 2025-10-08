from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

# -------------------- CONFIG --------------------
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
CHAT_MODEL = "deepseek-ai/DeepSeek-R1:fireworks-ai"
API_URL = f"https://api-inference.huggingface.co/models/{CHAT_MODEL}"

# -------------------- FASTAPI APP --------------------
app = FastAPI(title="FlashPress Chatbot")

# -------------------- REQUEST MODEL --------------------
class ChatRequest(BaseModel):
    message: str
    context: str = None

# -------------------- CHAT FUNCTION --------------------
def chat_with_ai(message: str, context: str = None) -> str:
    prompt = f"Context: {context}\nUser: {message}" if context else message
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.3,
            "max_new_tokens": 500,
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code != 200:
        print("HuggingFace API error:", response.text)
        return "AI chat model unavailable. Check your API key."
    
    data = response.json()
    
    # The HuggingFace model may return a list of dicts with 'generated_text'
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    else:
        return "AI returned an empty response."

# -------------------- ROUTE --------------------
@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    try:
        answer = chat_with_ai(chat_request.message, chat_request.context)
        return {"reply": answer}
    except Exception as e:
        print("Chat error:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
