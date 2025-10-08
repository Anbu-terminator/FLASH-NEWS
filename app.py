from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from routes.news import news_bp
from routes.summarizer import summarizer_bp
from routes.fake_news import fake_news_bp
from routes.chatbot import chatbot_bp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'default-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)

app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(summarizer_bp, url_prefix='/api/summarizer')
app.register_blueprint(fake_news_bp, url_prefix='/api/fake-news')
app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarizer')
def summarizer():
    return render_template('summarizer.html')

@app.route('/fake-news')
def fake_news():
    return render_template('fake_news.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
