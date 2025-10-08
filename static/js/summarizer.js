async function summarizeText() {
    const text = document.getElementById('text-input').value.trim();
    
    if (!text) {
        alert('Please enter some text to summarize');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    try {
        const response = await fetch('/api/summarizer/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.summary);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function summarizeUrl() {
    const url = document.getElementById('url-input').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    try {
        const response = await fetch('/api/summarizer/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.summary);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function summarizeYoutube() {
    const url = document.getElementById('youtube-input').value.trim();
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    try {
        const response = await fetch('/api/summarizer/youtube', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.summary);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function summarizePdf() {
    const fileInput = document.getElementById('pdf-input');
    const numPages = document.getElementById('num-pages').value;
    
    if (!fileInput.files[0]) {
        alert('Please select a PDF file');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('num_pages', numPages);
    
    try {
        const response = await fetch('/api/summarizer/pdf', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.summary);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function showLoading(show) {
    document.getElementById('loading-summary').style.display = show ? 'block' : 'none';
}

function showResult(summary) {
    document.getElementById('summary-text').textContent = summary;
    document.getElementById('summary-result').style.display = 'block';
}

function hideResult() {
    document.getElementById('summary-result').style.display = 'none';
}
