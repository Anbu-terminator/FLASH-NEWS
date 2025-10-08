from flask import Blueprint, jsonify, request
import requests
import os

news_bp = Blueprint('news', __name__)

news_data = {}

@news_bp.route('/fetch', methods=['GET'])
def fetch_news():
    api_key = os.getenv('NEWSDATA_API_KEY')
    category = request.args.get('category', '')
    
    try:
        url = f'https://newsdata.io/api/1/news?apikey={api_key}&language=en'
        if category:
            url += f'&category={category}'
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('results'):
            articles = []
            for article in data['results'][:20]:
                article_id = article.get('article_id', str(hash(article.get('title', ''))))
                articles.append({
                    'id': article_id,
                    'title': article.get('title', 'No Title'),
                    'description': article.get('description', 'No description available'),
                    'image': article.get('image_url', ''),
                    'url': article.get('link', '#'),
                    'source': article.get('source_name', 'Unknown'),
                    'pubDate': article.get('pubDate', ''),
                    'likes': news_data.get(article_id, {}).get('likes', 0),
                    'comments': news_data.get(article_id, {}).get('comments', [])
                })
            return jsonify({'success': True, 'articles': articles})
        else:
            return jsonify({'success': False, 'error': 'No articles found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@news_bp.route('/like', methods=['POST'])
def like_article():
    data = request.json
    article_id = data.get('article_id')
    
    if article_id not in news_data:
        news_data[article_id] = {'likes': 0, 'comments': []}
    
    news_data[article_id]['likes'] += 1
    
    return jsonify({'success': True, 'likes': news_data[article_id]['likes']})

@news_bp.route('/comment', methods=['POST'])
def add_comment():
    data = request.json
    article_id = data.get('article_id')
    comment = data.get('comment')
    
    if article_id not in news_data:
        news_data[article_id] = {'likes': 0, 'comments': []}
    
    news_data[article_id]['comments'].append(comment)
    
    return jsonify({'success': True, 'comments': news_data[article_id]['comments']})
