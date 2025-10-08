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

# ---------------------------
# HUGGINGFACE SUMMARIZER
# ---------------------------
def summarize_with_huggingface(text):
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    models = [
        "facebook/bart-large-cnn",
        "sshleifer/distilbart-cnn-12-6",
        "google/pegasus-xsum"
    ]
    
    # Limit length to avoid API overflow
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

            # Retry if model is still loading
            if response.status_code == 503:
                time.sleep(2)
                continue
        except Exception:
            continue
    
    # Fallback: return first 200 words
    words = text.split()[:200]
    return ' '.join(words) + '...'


# ---------------------------
# TEXT SUMMARIZER
# ---------------------------
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


# ---------------------------
# URL SUMMARIZER
# ---------------------------
@summarizer_bp.route('/url', methods=['POST'])
def summarize_url():
    try:
        data = request.json
        url = data.get('url', '')
        if not url:
            return jsonify({'success': False, 'error': 'No URL provided'})
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
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


# ---------------------------
# YOUTUBE SUMMARIZER (updated for latest library)
# ---------------------------
def extract_youtube_id(url):
    """Extract video ID from any YouTube link."""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be/([0-9A-Za-z_-]{11})',
        r'embed/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@summarizer_bp.route('/youtube', methods=['POST'])
def summarize_youtube():
    try:
        data = request.json or {}
        url = data.get('url', '')
        video_id = extract_youtube_id(url)
        
        if not video_id:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'}), 400

        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return jsonify({'success': False, 'error': 'Missing YouTube API key'}), 500

        # Fetch video details
        yt_api_url = (
            f"https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet&id={video_id}&key={api_key}"
        )
        resp = requests.get(yt_api_url)
        if resp.status_code != 200:
            return jsonify({'success': False, 'error': f"YouTube API error {resp.status_code}"}), 500

        data = resp.json()
        if not data.get('items'):
            return jsonify({'success': False, 'error': 'Video not found or private'}), 404

        snippet = data['items'][0]['snippet']
        title = snippet.get('title', '')
        description = snippet.get('description', '')

        if not title and not description:
            return jsonify({'success': False, 'error': 'No video metadata found'}), 404

        combined_text = f"{title}. {description}"
        summary = summarize_with_huggingface(combined_text[:5000])

        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ---------------------------
# PDF SUMMARIZER
# ---------------------------
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
