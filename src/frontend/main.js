// Configuration
// Placeholder __BACKEND_URL__ will be replaced during Docker deployment
const BACKEND_URL = '__BACKEND_URL__'.startsWith('http') ? '__BACKEND_URL__' : 'http://127.0.0.1:8000/api/chat';

// DOM Elements
const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// State
let isTyping = false;

// Event Listeners
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        sendMessage();
    }
});

function sendMessage() {
    const text = userInput.value.trim();
    if (!text || isTyping) return;

    // Add user message to UI
    appendMessage(text, 'user-message');
    userInput.value = '';

    // Simulate/Show typing indicator
    showTypingIndicator();

    // Send to backend
    fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        hideTypingIndicator();
        appendMessage(data.response, 'bot-message');
    })
    .catch(error => {
        hideTypingIndicator();
        appendMessage(`❌ Error: No se pudo conectar con el servidor (${error.message}). Asegúrate de que el backend está corriendo en ${BACKEND_URL}.`, 'bot-message error-message');
        console.error('Fetch error:', error);
    });
}

function appendMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    
    // Convert newlines to breaks or use innerText safely
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Simple markdown-like replacement for bold or just use text if simple
    if (className === 'bot-message') {
        console.log("🤖 Bot response:", text);
        const p = document.createElement('p');
        
        // Replace newlines and render images
        let html = text.replace(/\n/g, '<br>');
        
        // Extract base backend URL (without /api/chat)
        const backendBaseUrl = BACKEND_URL.replace('/api/chat', '');
        
        // Handle markdown images
        html = html.replace(/!\[(.*?)\]\((.*?)\)/g, `<img src="${backendBaseUrl}/api/$2" alt="$1" style="max-width: 100%; border-radius: 8px; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">`);
        
        // Handle raw HTML images if agent generated them
        html = html.replace(/src=["']chart\.png["']/g, `src="${backendBaseUrl}/api/chart.png"`);
        
        p.innerHTML = html;
        contentDiv.appendChild(p);
    } else {
        const p = document.createElement('p');
        p.textContent = text;
        contentDiv.appendChild(p);
    }

    messageDiv.appendChild(contentDiv);
    chatHistory.appendChild(messageDiv);
    
    // Auto-scroll
    setTimeout(() => {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }, 100);
}

function showTypingIndicator() {
    isTyping = true;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message typing-indicator-msg';
    messageDiv.id = 'typing-indicator-msg';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    
    contentDiv.appendChild(indicator);
    messageDiv.appendChild(contentDiv);
    chatHistory.appendChild(messageDiv);
    
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function hideTypingIndicator() {
    isTyping = false;
    const indicator = document.getElementById('typing-indicator-msg');
    if (indicator) {
        indicator.remove();
    }
}

// Homepage logic
document.getElementById('start-chat-btn').addEventListener('click', () => {
    const homepage = document.getElementById('homepage');
    homepage.style.opacity = '0';
    setTimeout(() => {
        homepage.style.display = 'none';
    }, 300);
});
