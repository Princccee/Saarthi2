document.addEventListener('DOMContentLoaded', function() {
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
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        toggleSendButton();
    });

    // Toggle send button based on input
    function toggleSendButton() {
        if (chatInput.value.trim() !== '') {
            sendBtn.classList.remove('disabled');
        } else {
            sendBtn.classList.add('disabled');
        }
    }

    // Handle sending a message
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;

        // Add user message to chat
        addMessage(message, 'user');

        // Reset input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        toggleSendButton();

        // Show assistant typing indicator
        showTypingIndicator();

        // Make real API call
        getRealResponse(message).then(response => {
            // Remove typing indicator
            const typingIndicator = document.querySelector('.typing-indicator-container');
            if (typingIndicator) typingIndicator.remove();

            // Show assistant response with streaming effect
            streamResponse(response);
        }).catch(error => {
            console.error('Error:', error);
            const typingIndicator = document.querySelector('.typing-indicator-container');
            if (typingIndicator) typingIndicator.remove();

            streamResponse("Sorry, there was an error processing your request.");
        });
    }


    // Add message to chat
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
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Show typing indicator
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

    // Stream response with typing effect
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
        
        let i = 0;
        const speed = 20; // ms per character
        
        function typeWriter() {
            if (i < fullResponse.length) {
                streamingText.textContent += fullResponse.charAt(i);
                i++;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                setTimeout(typeWriter, speed);
            } else {
                // Remove cursor when done typing
                cursor.remove();
            }
        }
        
        typeWriter();
    }


    // Get real response from backend
    function getRealResponse(message) {
        return fetch("http://127.0.0.1:5000/process", {
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

    // Create a new chat
    function startNewChat() {
        // Clear chat messages except the first welcome message
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
        
        // Update chat title
        document.querySelector('.chat-title').textContent = 'New Conversation';
    }

    // Event Listeners
    sendBtn.addEventListener('click', function() {
        if (!this.classList.contains('disabled')) {
            sendMessage();
        }
    });

    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.classList.contains('disabled')) {
                sendMessage();
            }
        }
    });

    micBtn.addEventListener('click', function() {
        alert('Speech recognition feature coming soon!');
        
        // Integration point for speech recognition API
        // Example:
        /*
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            
            recognition.start();
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                chatInput.value = transcript;
                chatInput.style.height = 'auto';
                chatInput.style.height = (chatInput.scrollHeight) + 'px';
                toggleSendButton();
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error', event.error);
                alert('Error recognizing speech. Please try again.');
            };
        } else {
            alert('Speech recognition is not supported in your browser.');
        }
        */
    });

    // Toggle sidebar on mobile
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('visible');
    });

    // Dark mode toggle
    themeToggle.addEventListener('change', function () {
        const isDark = this.checked;
        document.body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });

    // Load theme preference from localStorage if available
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.checked = true;
    } else {
        document.body.classList.remove('dark-mode');
        themeToggle.checked = false;
    }

    // New chat button
    newChatBtn.addEventListener('click', startNewChat);

    // Chat history items
    chatHistoryItems.forEach(item => {
        item.addEventListener('click', function() {
            const chatTitle = this.querySelector('span').textContent;
            document.querySelector('.chat-title').textContent = chatTitle;
            
            // If on mobile, hide sidebar after selection
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('visible');
            }
            
            // For a real app, you'd load the chat history here
            // For now, we'll just create a new chat
            startNewChat();
        });
    });

    // Load theme preference from localStorage if available
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        themeToggle.checked = true;
    }

    // Initialize
    toggleSendButton();
    
    // Focus input on page load
    chatInput.focus();
});