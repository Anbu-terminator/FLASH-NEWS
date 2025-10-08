from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

fake_news_bp = Blueprint('fake_news', __name__)

TRUSTED_SOURCES = [
    'thehindu.com', 'timesofdindia.indiatimes.com', 'indianexpress.com', 
    'hindustantimes.com', 'ndtv.com', 'business-standard.com', 'livemint.com',
    'economictimes.indiatimes.com', 'deccanherald.com', 'telegraphindia.com',
    'dnaindia.com', 'outlookindia.com', 'news18.com', 'ptinews.com',
    'dinathanthi.com', 'dinamalar.com', 'dinakaran.com', 'maalaimalar.com',
    'puthiyathalaimurai.com', 'polimernews.com', 'suntv.com', 'vikatan.com',
    'anandavikatan.com', 'manoramaonline.com', 'mathrubhumi.com', 
    'eenadu.net', 'sakshi.com', 'lokmat.com', 'gujaratsamachar.com',
    'erajasthanpatrika.com', 'punjabkesari.in', 'bbc.com', 'reuters.com',
    'apnews.com', 'theguardian.com', 'cnn.com', 'nytimes.com', 
    'washingtonpost.com', 'economist.com', 'ft.com', 'wsj.com',
    'bloomberg.com', 'aljazeera.com', 'news.sky.com', 'abcnews.go.com',
    'cbsnews.com', 'nbcnews.com', 'foxnews.com', 'thetimes.co.uk',
    'nature.com', 'sciencemag.org', 'techcrunch.com', 'wired.com',
    'theverge.com', 'forbes.com', 'cnet.com'
]

@fake_news_bp.route('/check', methods=['POST'])
def check_fake_news():
    try:
        data = request.json
        text = data.get('text', '')
        url = data.get('url', '')
        
        if url:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            domain = domain.replace('www.', '')
            
            is_trusted = any(trusted in domain for trusted in TRUSTED_SOURCES)
            
            if is_trusted:
                return jsonify({
                    'success': True,
                    'result': 'REAL',
                    'confidence': 'High',
                    'message': 'This source is from a trusted news outlet.'
                })
            else:
                return jsonify({
                    'success': True,
                    'result': 'UNVERIFIED',
                    'confidence': 'Medium',
                    'message': 'This source is not in our trusted list. Verify from multiple sources.'
                })
        
        elif text:
            text_lower = text.lower()
            
            fake_indicators = ['clickbait', 'shocking', 'you won\'t believe', 'miracle cure', 
                             'breaking:', 'urgent:', 'act now', 'limited time']
            
            indicator_count = sum(1 for indicator in fake_indicators if indicator in text_lower)
            
            if indicator_count >= 2:
                return jsonify({
                    'success': True,
                    'result': 'LIKELY FAKE',
                    'confidence': 'Medium',
                    'message': 'Text contains multiple sensational indicators. Verify from trusted sources.'
                })
            else:
                return jsonify({
                    'success': True,
                    'result': 'NEEDS VERIFICATION',
                    'confidence': 'Low',
                    'message': 'Unable to determine authenticity. Cross-check with trusted news sources.'
                })
        
        else:
            return jsonify({'success': False, 'error': 'No text or URL provided'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
