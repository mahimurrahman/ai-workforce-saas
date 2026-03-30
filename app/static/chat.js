// Chat application state
const chatState = {
    messages: [],
    isLoading: false,
    userId: 1,
};

// DOM elements
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.querySelector('.btn-clear');

// Agent emojis for visual identification
const agentEmojis = {
    support: '💬',
    sales: '🛍️',
    ops: '⚙️',
};

const agentLabels = {
    support: 'Support Agent',
    sales: 'Sales Agent',
    ops: 'Ops Agent',
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Focus input on load
    messageInput.focus();
    
    // Setup event listeners
    chatForm.addEventListener('submit', handleSendMessage);
    clearBtn.addEventListener('click', handleClearChat);
    
    // Allow Shift+Enter for newline, Enter to send
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});

// Handle sending a message
async function handleSendMessage(e) {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    if (!message || chatState.isLoading) return;
    
    // Disable send while loading
    chatState.isLoading = true;
    sendBtn.disabled = true;
    messageInput.disabled = true;
    
    // Add user message to UI
    addMessage('user', message);
    chatState.messages.push({ role: 'user', content: message });
    
    // Clear input
    messageInput.value = '';
    messageInput.focus();
    
    try {
        // Send to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_id: chatState.userId, 
                message: message 
            }),
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Add AI message
        addMessage('ai', data.response, data.agent_type, data.confidence);
        chatState.messages.push({ 
            role: 'ai', 
            content: data.response, 
            agent_type: data.agent_type,
            confidence: data.confidence 
        });
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('error', `Error: ${error.message}`);
    } finally {
        // Re-enable send
        chatState.isLoading = false;
        sendBtn.disabled = false;
        messageInput.disabled = false;
        messageInput.focus();
    }
}

// Add message to UI
function addMessage(type, content, agentType = null, confidence = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    let html = '';
    
    if (type === 'user') {
        html = `
            <div class="message-content">
                <p>${escapeHtml(content)}</p>
            </div>
        `;
    } else if (type === 'ai') {
        const emoji = agentEmojis[agentType] || '🤖';
        const label = agentLabels[agentType] || 'AI Agent';
        const confidencePercent = Math.round(confidence * 100);
        
        html = `
            <div class="message-header">
                <span class="agent-badge">
                    <span class="agent-emoji">${emoji}</span>
                    ${label}
                </span>
                <span class="confidence">${confidencePercent}% confident</span>
            </div>
            <div class="message-content">
                <p>${escapeHtml(content)}</p>
            </div>
        `;
    } else if (type === 'error') {
        html = `
            <div class="message-content error-message">
                <p>${escapeHtml(content)}</p>
            </div>
        `;
    }
    
    messageDiv.innerHTML = html;
    messagesContainer.appendChild(messageDiv);
    
    // Auto-scroll to latest message
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}

// Clear chat history
function handleClearChat() {
    if (confirm('Clear all messages? This cannot be undone.')) {
        chatState.messages = [];
        messagesContainer.innerHTML = `
            <div class="message system">
                <div class="message-content">
                    <p>Chat cleared. Start a new conversation!</p>
                </div>
            </div>
        `;
        messageInput.focus();
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
