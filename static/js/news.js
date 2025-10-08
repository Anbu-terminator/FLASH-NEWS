let currentCategory = '';

document.addEventListener('DOMContentLoaded', () => {
    loadNews('');
    
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            loadNews(currentCategory);
        });
    });
});

async function loadNews(category) {
    const loading = document.getElementById('loading');
    const container = document.getElementById('news-container');
    
    loading.style.display = 'block';
    container.innerHTML = '';
    
    try {
        const response = await fetch(`/api/news/fetch?category=${category}`);
        const data = await response.json();
        
        if (data.success && data.articles) {
            displayNews(data.articles);
        } else {
            container.innerHTML = `<div class="col-12"><div class="alert alert-warning">${data.error || 'No news found'}</div></div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error loading news: ${error.message}</div></div>`;
    } finally {
        loading.style.display = 'none';
    }
}

function displayNews(articles) {
    const container = document.getElementById('news-container');
    
    articles.forEach((article, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 fade-in';
        col.style.animationDelay = `${index * 0.1}s`;
        
        col.innerHTML = `
            <div class="card news-card shadow-sm">
                ${article.image ? `<img src="${article.image}" class="card-img-top" alt="${article.title}">` : ''}
                <div class="card-body">
                    <h5 class="card-title">${article.title}</h5>
                    <p class="card-text">${article.description || 'No description available'}</p>
                    <p class="text-muted small mb-2">
                        <i class="bi bi-newspaper"></i> ${article.source}
                        ${article.pubDate ? `<br><i class="bi bi-clock"></i> ${new Date(article.pubDate).toLocaleDateString()}` : ''}
                    </p>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary" onclick="likeArticle('${article.id}', this)">
                                <i class="bi bi-hand-thumbs-up"></i> <span class="like-count">${article.likes || 0}</span>
                            </button>
                            <button class="btn btn-sm btn-outline-primary" onclick="showCommentBox('${article.id}')">
                                <i class="bi bi-chat"></i> ${article.comments?.length || 0}
                            </button>
                        </div>
                        <div class="btn-group">
                            <a href="${article.url}" target="_blank" class="btn btn-sm btn-primary">Read</a>
                            <button class="btn btn-sm btn-success" onclick="shareArticle('${article.url}', '${article.title}')">
                                <i class="bi bi-share"></i>
                            </button>
                        </div>
                    </div>
                    <div id="comment-box-${article.id}" style="display:none;" class="mt-3">
                        <input type="text" class="form-control form-control-sm mb-2" id="comment-input-${article.id}" placeholder="Add a comment...">
                        <button class="btn btn-sm btn-primary" onclick="addComment('${article.id}')">Post</button>
                    </div>
                    <div id="comments-${article.id}" class="mt-2"></div>
                </div>
            </div>
        `;
        
        container.appendChild(col);
    });
}

async function likeArticle(articleId, btn) {
    try {
        const response = await fetch('/api/news/like', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ article_id: articleId })
        });
        const data = await response.json();
        
        if (data.success) {
            btn.querySelector('.like-count').textContent = data.likes;
        }
    } catch (error) {
        console.error('Error liking article:', error);
    }
}

function showCommentBox(articleId) {
    const box = document.getElementById(`comment-box-${articleId}`);
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

async function addComment(articleId) {
    const input = document.getElementById(`comment-input-${articleId}`);
    const comment = input.value.trim();
    
    if (!comment) return;
    
    try {
        const response = await fetch('/api/news/comment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ article_id: articleId, comment })
        });
        const data = await response.json();
        
        if (data.success) {
            input.value = '';
            displayComments(articleId, data.comments);
        }
    } catch (error) {
        console.error('Error adding comment:', error);
    }
}

function displayComments(articleId, comments) {
    const container = document.getElementById(`comments-${articleId}`);
    container.innerHTML = comments.map(c => `<div class="small text-muted">💬 ${c}</div>`).join('');
}

function shareArticle(url, title) {
    const text = encodeURIComponent(`Check out this news: ${title}`);
    const link = encodeURIComponent(url);
    
    const whatsappUrl = `https://wa.me/?text=${text}%20${link}`;
    window.open(whatsappUrl, '_blank');
}
