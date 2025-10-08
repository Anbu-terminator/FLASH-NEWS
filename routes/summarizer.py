from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import PyPDF2
import os
import io
import re
import time

summarizer_bp = Blueprint('summarizer', __name__)

def summarize_with_huggingface(text):
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    # Try multiple summarization models with fallback
    models = [
        "facebook/bart-large-cnn",
        "sshleifer/distilbart-cnn-12-6",
        "google/pegasus-xsum"
    ]
    
    # Truncate text to manageable size
    max_length = 1024
    text = text[:max_length * 3]
    
    for model in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": 150,
                    "min_length": 30,
                    "do_sample": False
                },
                "options": {"wait_for_model": True}
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary = result[0].get('summary_text', '')
                    if summary:
                        return summary
                elif isinstance(result, dict):
                    summary = result.get('summary_text', result.get('generated_text', ''))
                    if summary:
                        return summary
            
            # If model is loading, wait and retry
            if response.status_code == 503:
                time.sleep(2)
                continue
                
        except Exception:
            continue
    
    # Fallback: return first 200 words
    words = text.split()[:200]
    return ' '.join(words) + '...'

@summarizer_bp.route('/text', methods=['POST'])
def summarize_text():
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'No text provided'})
        
        summary = summarize_with_huggingface(text)
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@summarizer_bp.route('/url', methods=['POST'])
def summarize_url():
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'})
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        if not text:
            return jsonify({'success': False, 'error': 'Could not extract text from URL'})
        
        summary = summarize_with_huggingface(text[:5000])
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@summarizer_bp.route('/youtube', methods=['POST'])
def summarize_youtube():
    try:
        data = request.json
        url = data.get('url', '')
        
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'})
        
        video_id = video_id_match.group(1)
        
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([item['text'] for item in transcript_list])
        
        summary = summarize_with_huggingface(transcript_text[:5000])
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@summarizer_bp.route('/pdf', methods=['POST'])
def summarize_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        num_pages = int(request.form.get('num_pages', 5))
        
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        
        text = ''
        for i in range(min(num_pages, len(pdf_reader.pages))):
            page = pdf_reader.pages[i]
            text += page.extract_text() + ' '
        
        if not text.strip():
            return jsonify({'success': False, 'error': 'Could not extract text from PDF'})
        
        summary = summarize_with_huggingface(text[:5000])
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
