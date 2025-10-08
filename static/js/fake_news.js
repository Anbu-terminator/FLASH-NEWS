async function checkText() {
    const text = document.getElementById('text-check-input').value.trim();
    
    if (!text) {
        alert('Please enter some text to check');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    try {
        const response = await fetch('/api/fake-news/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.result, data.message, data.confidence);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function checkUrl() {
    const url = document.getElementById('url-check-input').value.trim();
    
    if (!url) {
        alert('Please enter a URL to check');
        return;
    }
    
    showLoading(true);
    hideResult();
    
    try {
        const response = await fetch('/api/fake-news/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await response.json();
        
        if (data.success) {
            showResult(data.result, data.message, data.confidence);
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
    document.getElementById('loading-check').style.display = show ? 'block' : 'none';
}

function showResult(result, message, confidence) {
    const resultAlert = document.getElementById('result-alert');
    const resultStatus = document.getElementById('result-status');
    const resultMessage = document.getElementById('result-message');
    const resultConfidence = document.getElementById('result-confidence');
    
    resultStatus.textContent = result;
    resultMessage.textContent = message;
    resultConfidence.textContent = `Confidence: ${confidence}`;
    
    resultAlert.className = 'alert';
    if (result === 'REAL') {
        resultAlert.classList.add('alert-success');
    } else if (result === 'UNVERIFIED' || result === 'NEEDS VERIFICATION') {
        resultAlert.classList.add('alert-warning');
    } else {
        resultAlert.classList.add('alert-danger');
    }
    
    document.getElementById('check-result').style.display = 'block';
}

function hideResult() {
    document.getElementById('check-result').style.display = 'none';
}
