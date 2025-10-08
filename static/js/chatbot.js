const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    addMessage(message, 'user');
    chatInput.value = '';
    
    const loadingId = addMessage('Thinking...', 'bot', true);
    
    try {
        const response = await fetch('/api/chatbot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        
        removeMessage(loadingId);
        
        if (data.success) {
            addMessage(data.response, 'bot');
        } else {
            addMessage('Error: ' + data.error, 'bot');
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('Error: ' + error.message, 'bot');
    }
}

function addMessage(text, sender, isLoading = false) {
    if (chatContainer.querySelector('.text-muted')) {
        chatContainer.innerHTML = '';
    }
    
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now();
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${sender}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    if (isLoading) {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>${text}</span>
            </div>
            <small class="d-block mt-1 opacity-75">${time}</small>
        `;
    } else {
        messageDiv.innerHTML = `
            <div>${text}</div>
            <small class="d-block mt-1 opacity-75">${time}</small>
        `;
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}
