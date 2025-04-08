document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const chatMessages = document.getElementById('chat-messages');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const themeToggle = document.getElementById('theme-toggle');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const chatHistoryItems = document.querySelectorAll('.chat-history-item');

    // Auto-resize textarea as user types
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        toggleSendButton();
    });

    function toggleSendButton() {
        if (chatInput.value.trim() !== '') {
            sendBtn.classList.remove('disabled');
        } else {
            sendBtn.classList.add('disabled');
        }
    }

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;

        addMessage(message, 'user');

        chatInput.value = '';
        chatInput.style.height = 'auto';
        toggleSendButton();

        showTypingIndicator();

        getRealResponse(message).then(response => {
            const typingIndicator = document.querySelector('.typing-indicator-container');
            if (typingIndicator) typingIndicator.remove();

            streamResponse(response);
        }).catch(error => {
            console.error('Error:', error);
            const typingIndicator = document.querySelector('.typing-indicator-container');
            if (typingIndicator) typingIndicator.remove();

            streamResponse("Sorry, there was an error processing your request.");
        });
    }

    function addMessage(content, sender) {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);

        const avatarIcon = sender === 'user' ? 'user' : 'robot';

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${avatarIcon}"></i>
            </div>
            <div>
                <div class="message-content">
                    ${content}
                </div>
                <div class="message-meta">
                    <span>Today, ${timeString}</span>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'assistant-message', 'typing-indicator-container');

        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;

        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function markdownToHTML(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/(\*\*|__)(.*?)\1/gim, '<strong>$2</strong>')
            .replace(/(\*|_)(.*?)\1/gim, '<em>$2</em>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/^\- (.*$)/gim, '<li>$1</li>')
            .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')
            .replace(/\n{2,}/g, '<br/><br/>')
            .replace(/\n/g, '<br/>');
    }

    function streamResponse(fullResponse) {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'assistant-message');

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div>
                <div class="message-content">
                    <span class="streaming-text"></span><span class="cursor-blink"></span>
                </div>
                <div class="message-meta">
                    <span>Today, ${timeString}</span>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        const streamingText = messageDiv.querySelector('.streaming-text');
        const cursor = messageDiv.querySelector('.cursor-blink');

        let formattedHTML = markdownToHTML(fullResponse.replace(/<br\s*\/?>/gi, '\n'));
        streamingText.innerHTML = formattedHTML;
        cursor.remove();
    }

    function getRealResponse(message) {
        return fetch("/process", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: message }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Server error");
                }
                return response.json();
            })
            .then(data => data.response);
    }

    function startNewChat() {
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }

        document.querySelector('.chat-title').textContent = 'New Conversation';
    }

    sendBtn.addEventListener('click', function () {
        if (!this.classList.contains('disabled')) {
            sendMessage();
        }
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.classList.contains('disabled')) {
                sendMessage();
            }
        }
    });

    micBtn.addEventListener('click', function () {
        alert('Speech recognition feature coming soon!');
    });

    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('visible');
    });

    themeToggle.addEventListener('change', function () {
        const isDark = this.checked;
        document.body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.checked = true;
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.checked = false;
    }

    newChatBtn.addEventListener('click', startNewChat);

    chatHistoryItems.forEach(item => {
        item.addEventListener('click', function () {
            const chatTitle = this.querySelector('span').textContent;
            document.querySelector('.chat-title').textContent = chatTitle;

            if (window.innerWidth <= 768) {
                sidebar.classList.remove('visible');
            }

            startNewChat();
        });
    });

    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.checked = true;
    }

    toggleSendButton();
    chatInput.focus();
});